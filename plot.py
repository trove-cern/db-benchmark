import os
import os.path as op
import re
import sys
import time
import datetime
from collections import namedtuple

import numpy as np

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

Benchmark = namedtuple("Benchmark", ["machine", "threads", "transaction_speed", "query_speed"])


def load_benchmarks():
    from_dir = "latest"
    if len(sys.argv) > 1:
        if not sys.argv[1] == "pin":
            from_dir = sys.argv[1]
        
    yield from_dir
    
    with open(op.join(from_dir, ".timestamp"), "r") as timestamp:
        yield int(timestamp.read().strip())

    with open(op.join(from_dir, ".benchmark"), "r") as benchmark_type:
        yield benchmark_type.read().strip()
    
    with open(op.join(from_dir, ".runtime"), "r") as runtime:
        yield runtime.read().strip()
    
    with open(op.join(from_dir, ".tablesize"), "r") as tablesize:
        yield tablesize.read().strip()
    
    data_files = [file for file in os.listdir(from_dir) if file.startswith("sb")]
    for file_name in data_files:
        machine = re.findall("sb-(.*)-", file_name)[0]
        threads = int(re.findall("-(\d+)", file_name)[0])
        
        with open(op.join(from_dir, file_name), "r") as file:
            data = file.read()
            speeds = list(map(float, re.findall("(\d+[\.]?\d*) per sec", data)))
            try:
                transaction_speed, query_speed, *_ = speeds
            except ValueError:
                continue
            yield Benchmark(machine, threads, transaction_speed, query_speed)
            

def plot():
    from_dir, timestamp, benchmark_type, runtime, tablesize, *benchmarks = list(load_benchmarks())

    machine_names = []

    for benchmark in benchmarks:
        print(benchmark)
        if benchmark.machine not in machine_names:
            machine_names.append(benchmark.machine)
    
    N = len({benchmark.machine for benchmark in benchmarks})
    width = 0.15
    ind = np.arange(N)
    
    fig, ax = plt.subplots()
    
    threads_tested = set()
    for benchmark in benchmarks:
        threads_tested.add(benchmark.threads)

    legend_1 = []
    legend_2 = []
    
    for i, threads in enumerate(sorted(threads_tested)):
        relevant_threads = [bm.query_speed for bm in benchmarks if bm.threads == threads]
        rects = ax.bar(ind+(i*width)-(width*((len(threads_tested)/2)-1)), relevant_threads, width)
        legend_1.append(rects[0])
        legend_2.append(threads)
    
    title_date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%b-%d %H:%M:%S")
    ax.set_title("Database benchmarks {}\nruntime={}s | table_rows={}\n{} | {}".format(benchmark_type, runtime, tablesize, timestamp, title_date))
    ax.legend(legend_1, ["{} threads".format(threads) for threads in legend_2])
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels(machine_names)
    ax.set_ylabel("Queries per second")
    ax.set_xlabel("Database storage type")

    fig.tight_layout()
            
    name = str(int(time.time()))
    plt.savefig("output_plots/{}.png".format(name))
    plt.savefig(op.join(from_dir, "{}.png".format(name)))
    
    if "pin" in sys.argv:
        plt.savefig("output_plots/pinned/{}.png".format(name))

if __name__ == "__main__":
    plot()
