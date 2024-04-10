from scipy.stats import gamma
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
from scipy.stats import genextreme, dgamma
import pandas as pd
import os


def get_best_distribution(data):
    dist_names = [
        "alpha",
        "anglit",
        "arcsine",
        "argus",
        "beta",
        "betaprime",
        "bradford",
        "burr",
        "burr12",
        "cauchy",
        "chi",
        "chi2",
        "cosine",
        "crystalball",
        "dgamma",
        "dweibull",
        "erlang",
        "expon",
        "exponnorm",
        "exponpow",
        "exponweib",
        "f",
        "fatiguelife",
        "fisk",
        "foldcauchy",
        "foldnorm",
        "gamma",
        "gausshyper",
        "genexpon",
        "genextreme",
        "gengamma",
        "genhalflogistic",
        "genlogistic",
        "genpareto",
        "gilbrat",
        "gompertz",
        "gumbel_l",
        "gumbel_r",
        "halfcauchy",
        "halfgennorm",
        "halflogistic",
        "halfnorm",
        "hypsecant",
        "invgamma",
        "invgauss",
        "invweibull",
        "johnsonsb",
        "johnsonsu",
        "kappa4",
        "kappa3",
        "ksone",
        "kstwobign",
        "laplace",
        "levy",
        "levy_l",
        "loggamma",
        "logistic",
        "loglaplace",
        "lognorm",
        "lomax",
        "maxwell",
        "mielke",
        "moyal",
        "nakagami",
        "ncf",
        "nct",
        "ncx2",
        "norm",
        "norminvgauss",
        "pareto",
        "pearson3",
        "powerlaw",
        "powerlognorm",
        "powernorm",
        "rdist",
        "reciprocal",
        "rayleigh",
        "rice",
        "recipinvgauss",
        "semicircular",
        "skewnorm",
        "t",
        "triang",
        "truncexpon",
        "truncnorm",
        "tukeylambda",
        "uniform",
        "vonmises",
        "vonmises_line",
        "wald",
        "weibull_max",
        "weibull_min",
        "wrapcauchy",
    ]
    dist_results = []
    params = {}
    for dist_name in dist_names:
        dist = getattr(st, dist_name)
        param = dist.fit(data)

        params[dist_name] = param
        D, p = st.kstest(data, dist_name, args=param)
        dist_results.append((dist_name, p))

    best_dist, best_p = max(dist_results, key=lambda item: item[1])

    return best_dist, best_p, params[best_dist]


def plot_results(from_centr, to_centr):

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.hist(
        np.arange(len(from_centr)),
        bins=len(from_centr),
        weights=from_centr,
        color="green",
        edgecolor="black",
    )
    plt.title("from centr")
    plt.xlabel("Index")
    plt.ylabel("Value")

    plt.subplot(1, 2, 2)
    plt.hist(
        np.arange(len(to_centr)),
        bins=len(to_centr),
        weights=to_centr,
        color="blue",
        edgecolor="black",
    )
    plt.title("to centr")
    plt.xlabel("Index")
    plt.ylabel("Value")

    plt.tight_layout()
    plt.show()


def read_data(filename):
    data = pd.read_csv(filename, delimiter=";")
    return data


def generate_hourly_traffic(output_file, data, comaprision_data):
    daily_data = sum(comaprision_data)
    hours_proportion = [x / daily_data for x in comaprision_data]

    for column in data.columns[1:]:
        data[column] = data[column].apply(
            lambda x: [int(np.round(x * proportion)) for proportion in hours_proportion]
        )

    data.to_csv(output_file, index=False)


def main():
    warsaw_data_to_centr = [
        16761,
        10763,
        8476,
        9992,
        18244,
        59692,
        132420,
        180122,
        176562,
        159092,
        144468,
        140903,
        140905,
        140372,
        143619,
        147331,
        143925,
        138387,
        134373,
        116887,
        94305,
        70799,
        51097,
        31789,
    ]
    warsaw_data_from_centr = [
        19469,
        11867,
        8658,
        8984,
        14015,
        37843,
        84042,
        126436,
        133454,
        126932,
        127679,
        132823,
        138030,
        144400,
        159680,
        174373,
        172197,
        166619,
        157786,
        135847,
        112138,
        85603,
        64211,
        27356,
    ]
    data = read_data("networks/wielun/daily_traffic.csv")
    generate_hourly_traffic(
        "networks/wielun/hourly_traffic_to_centr.csv", data.copy(), warsaw_data_to_centr
    )
    generate_hourly_traffic(
        "networks/wielun/hourly_traffic_from_centr.csv",
        data.copy(),
        warsaw_data_from_centr,
    )


if __name__ == "__main__":
    main()
