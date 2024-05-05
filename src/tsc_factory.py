from src.trafficsignal.uniformcycletsc import UniformCycleTSC
from src.trafficsignal.websterstsc import WebstersTSC
from src.trafficsignal.maxpressuretsc import MaxPressureTSC
from src.trafficsignal.sotltsc import SOTLTSC


def tsc_factory(
    tsc_type, tl, args, netdata, rl_stats, exp_replay, neural_network, eps, conn
):
    if tsc_type == "websters":
        return WebstersTSC(
            conn,
            tl,
            args.mode,
            netdata,
            args.r,
            args.y,
            args.g_min,
            args.c_min,
            args.c_max,
            args.sat_flow,
            args.update_freq,
        )
    elif tsc_type == "sotl":
        return SOTLTSC(
            conn,
            tl,
            args.mode,
            netdata,
            args.r,
            args.y,
            args.g_min,
            args.theta,
            args.omega,
            args.mu,
        )
    elif tsc_type == "uniform":
        return UniformCycleTSC(conn, tl, args.mode, netdata, args.r, args.y, args.g_min)
    elif tsc_type == "maxpressure":
        return MaxPressureTSC(conn, tl, args.mode, netdata, args.r, args.y, args.g_min)
    else:
        assert 0, (
            "Supplied traffic signal control argument type "
            + str(tsc)
            + " does not exist."
        )
