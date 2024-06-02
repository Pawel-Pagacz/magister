import os
import sys
import traci
import numpy as np

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
    from sumolib import checkBinary
    import sumolib
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


class NetworkData:
    def __init__(self, net_fp):
        self.net = sumolib.net.readNet(net_fp)
        print(self.net)
        self.edge_data = self.get_edge_data(self.net)
        self.lane_data = self.get_lane_data(self.net)
        self.node_data, self.intersection_data = self.get_node_data(self.net)
        print("SUCCESSFULLY GENERATED NET DATA")

    def get_net_data(self):
        return {
            "lane": self.lane_data,
            "edge": self.edge_data,
            "node": self.node_data,
            "inter": self.intersection_data,
        }

    def get_edge_data(self, net):
        edges = net.getEdges()
        edge_data = {str(edge.getID()): {} for edge in edges}

        for edge in edges:
            edge_ID = str(edge.getID())
            edge_data[edge_ID]["lanes"] = [
                str(lane.getID()) for lane in edge.getLanes()
            ]
            edge_data[edge_ID]["length"] = float(edge.getLength())
            edge_data[edge_ID]["outgoing"] = [
                str(out.getID()) for out in edge.getOutgoing()
            ]
            edge_data[edge_ID]["noutgoing"] = len(edge_data[edge_ID]["outgoing"])
            edge_data[edge_ID]["nlanes"] = len(edge_data[edge_ID]["lanes"])
            edge_data[edge_ID]["incoming"] = [
                str(inc.getID()) for inc in edge.getIncoming()
            ]
            edge_data[edge_ID]["outnode"] = str(edge.getFromNode().getID())
            edge_data[edge_ID]["incnode"] = str(edge.getToNode().getID())
            edge_data[edge_ID]["speed"] = float(edge.getSpeed())

        return edge_data

    def get_lane_data(self, net):
        lane_ids = []
        for edge in self.edge_data:
            lane_ids.extend(self.edge_data[edge]["lanes"])

        lanes = [net.getLane(lane) for lane in lane_ids]

        lane_data = {lane: {} for lane in lane_ids}

        for lane in lanes:
            lane_id = lane.getID()
            lane_data[lane_id]["length"] = lane.getLength()
            lane_data[lane_id]["speed"] = lane.getSpeed()
            lane_data[lane_id]["edge"] = str(lane.getEdge().getID())
            lane_data[lane_id]["outgoing"] = {}
            moveid = []
            for conn in lane.getOutgoing():
                out_id = str(conn.getToLane().getID())
                lane_data[lane_id]["outgoing"][out_id] = {
                    "dir": str(conn.getDirection()),
                    "index": conn.getTLLinkIndex(),
                }
                moveid.append(str(conn.getDirection()))
            lane_data[lane_id]["movement"] = "".join(sorted(moveid))
            lane_data[lane_id]["incoming"] = []

        for lane in lane_data:
            for inc in lane_data:
                if lane == inc:
                    continue
                else:
                    if inc in lane_data[lane]["outgoing"]:
                        lane_data[inc]["incoming"].append(lane)

        return lane_data

    def get_node_data(self, net):
        nodes = net.getNodes()
        node_data = {node.getID(): {} for node in nodes}

        for node in nodes:
            node_id = node.getID()
            node_data[node_id]["incoming"] = set(
                str(edge.getID()) for edge in node.getIncoming()
            )
            node_data[node_id]["outgoing"] = set(
                str(edge.getID()) for edge in node.getOutgoing()
            )
            node_data[node_id]["tlsindex"] = {
                conn.getTLLinkIndex(): str(conn.getFromLane().getID())
                for conn in node.getConnections()
            }
            node_data[node_id]["tlsindexdir"] = {
                conn.getTLLinkIndex(): str(conn.getDirection())
                for conn in node.getConnections()
            }

        intersection_data = {
            str(node): node_data[node]
            for node in node_data
            if "traffic_light" in net.getNode(node).getType()
        }

        return node_data, intersection_data


def get_queue_length(intersection_data):
    queue_lengths = {}

    for intersection in intersection_data:
        incoming_lanes = list(intersection_data[intersection]["incoming"])
        total_queue = 0
        lane_count = 0

        for lane in incoming_lanes:
            vehicle_ids = traci.lane.getLastStepVehicleIDs(lane)
            queue_length = sum(
                1 for v in vehicle_ids if traci.vehicle.getSpeed(v) < 0.3
            )
            total_queue += queue_length
            lane_count += 1

        average_queue = total_queue / lane_count if lane_count > 0 else 0
        queue_lengths[intersection] = average_queue

    return queue_lengths
