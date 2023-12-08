<template>
  <div class="chart-container-sankey" ref="sankeyContainer">
    <svg id="sankey-svg" width="100%" height="100%">
    </svg>
  </div>
</template>

<script lang="ts">
import * as d3 from 'd3';
import { sankey as d3Sankey, sankeyLinkHorizontal as d3SankeyLinkHorizontal } from 'd3-sankey';
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';

interface DataDistrib {
  model: string;
  role: string;
  toxicity: string;
  cluster: number;
  turn: number;
  value: number;
}

interface Node {
  name: string;
}

interface Link {
  source: number;
  target: number;
  names: [string, string];
  value: number;
}

export default {
  name: 'Sankey',
  data() {
    return {
      chartData: [] as DataDistrib[],
      sankeyData: {
        nodes: [] as Node[],
        links: [] as Link[],
      },
      size: { width: 700, height: 300 } as ComponentSize,
      margin: { left: 50, right: 40, top: 40, bottom: 60 } as Margin,
    }
  },
  computed: {
    // Re-render the chart whenever the window is resized or the data changes (and data is non-empty)
    rerender() {
      return (!isEmpty(this.sankeyData)) && this.size
    }
  },
  async created() {
    const rawData = await d3.csv("../../data/proc/palm-2.csv");
    const parsedSet = d3.rollup(
      rawData,
      (v) => v.length,
      // (d) => d.model,
      (d) => d.role, // can there be more toxic messages from one-specific role?
      (d) => (d.toxicity).toString() == "True"? "Toxic" : "Non-Toxic",
      (d) => "Cluster " + (d.cluster).toString() + ": " + (d.cluster_summary).toString(),
      // (d) => "Turn " + (d.turn).toString()
    );
    const parsedData = this.unroll(
      parsedSet,
      ["role", "toxicity", "cluster"],
      "value"
    );
    this.create_sankey_data(parsedData, Object.keys(parsedData[0]));
  },
  methods: {
    onResize() {
      let target = this.$refs.sankeyContainer as HTMLElement;
      if (target === undefined) return;
      this.size = { width: target.clientWidth, height: target.clientHeight };
    },
    unroll(rollup: d3.InternMap, keys: string | any[], label = "value", p = {}): Array<any> {
      return Array.from(rollup, ([key, value]) =>
        value instanceof Map
          ? this.unroll(value, keys.slice(1), label, Object.assign({}, { ...p, [keys[0]]: key }))
          : Object.assign({}, { ...p, [keys[0]]: key, [label]: value })
      ).flat();
    },
    create_sankey_data(data: DataDistrib[], columns: Array<string>): void {
      console.log("Let's create some data for Sankey ...");
      const keys = columns.slice(0, -1);
      let index = -1;
      const nodes: Node[] = [];
      const nodeByKey = new Map();
      const indexByKey = new Map();
      const links: Link[] = [];
      const linkByKey = new Map();

      const nodeKey = ([key, value]: [string, any]) => `${key}-${value}`;
      const linkKey = (names: string[]) => names.join('→');

      const getValue = (d: DataDistrib, key: string): string | number | boolean => {
        return (d as any)[key]; // Type assertion here.
      };

      for (const k of keys) {
        for (const d of data) {
          const key = [k, getValue(d, k)];
          if (nodeByKey.has(nodeKey(key as [string, any]))) continue;
          const node = { name: getValue(d, k) };
          nodes.push({ name: node.name } as Node);
          nodeByKey.set(nodeKey(key as [string, any]), node);

          indexByKey.set(nodeKey(key as [string, any]), ++index);
        }
      }

      for (let i = 1; i < keys.length; ++i) {
        const a = keys[i - 1];
        const b = keys[i];
        const prefix = keys.slice(0, i + 1);

        for (const d of data) {
          const names = prefix.map(k => getValue(d, k));
          const value = d.value || 1;
          let link = linkByKey.get(linkKey(names.map((name) => name.toString())));
          if (link) {
            link.value += value;
            continue;
          }
          link = {
            source: indexByKey.get(nodeKey([a, getValue(d, a)])),
            target: indexByKey.get(nodeKey([b, getValue(d, b)])),
            names,
            value
          };
          links.push(link);
          linkByKey.set(linkKey(names.map(name => name.toString())), link);
        }
      }

      this.sankeyData = { nodes, links };
      console.log("sankey data: ", this.sankeyData);
    },
    initChart(): void {
      const width = this.size.width;
      const height = this.size.height;

      const sankey = d3Sankey()
        .nodeSort(null)
        .linkSort(null)
        .nodeWidth(4)
        .nodePadding(20)
        .extent([[0, 5], [width, height - 5]])

      const color = d3.scaleOrdinal(["user"], ["#87b5ff"]).unknown("#ccc");
      // const color = d3.scaleOrdinal(["user","assistant"], ["#1f77b4", "#ff7f0e"]).unknown("#ccc");
      const svg = d3.select("#sankey-svg")
        .attr("viewBox", [0, 0, width, height + 20])
        .attr("width", width)
        .attr("height", height )
        .attr("style", "max-width: 100%; height: auto;");

      svg.append("text")
        .attr("x", width / 2)
        .attr("y", height)
        .attr("fill", "currentColor")
        .attr("font-size", "15px")
        .attr("font-weight", "bold")
        .attr("text-anchor", "middle")
        .text("Relation between toxicity and message clusters");

      const { nodes, links } = sankey({
        nodes: this.sankeyData.nodes.map(d => Object.create(d)),
        links: this.sankeyData.links.map(d => Object.create(d))
      });

      svg.append("g")
        .selectAll("rect")
        .data(nodes)
        .join("rect")
        .attr("x", d => d.x0)
        .attr("y", d => d.y0)
        .attr("height", d => d.y1 - d.y0)
        .attr("width", d => d.x1 - d.x0)
        .append("title")
        .text(d => `${d.name}\n${d.value.toLocaleString()}`);

      svg.append("g")
        .attr("fill", "none")
        .selectAll("g")
        .data(links)
        .join("path")
        .attr("d", d3SankeyLinkHorizontal())
        .attr("stroke", d => color(d.names[0]))
        .attr("stroke-width", d => d.width)
        .style("mix-blend-mode", "multiply")
        .append("title")
        .text(d => `${d.names.join(" → ")}\n${d.value.toLocaleString()}`);

      svg.append("g")
        .style("font", "12px sans-serif")
        .selectAll("text")
        .data(nodes)
        .join("text")
        .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
        .attr("y", d => (d.y1 + d.y0) / 2)
        .attr("dy", "0.35em")
        .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
        .text(d => d.name)
        .append("tspan")
        .attr("fill-opacity", 0.7)
        .text(d => ` ${d.value}`);
    }
  },
  mounted() {
    window.addEventListener('resize', debounce(this.onResize, 100))
    this.onResize()
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize)
  },
  watch: {
    rerender(newSize) {
      if (!isEmpty(newSize)) {
        d3.select('#sankey-svg').selectAll('*').remove() // Clean all the elements in the chart
        this.initChart()
      }
    }
  },
};
</script>

<style scoped>
.chart-container-sankey {
    height: 100%;
}
</style>