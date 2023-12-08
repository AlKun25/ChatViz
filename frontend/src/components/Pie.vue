<template>
    <div class="chart-container-donut" ref="donutContainer">
        <svg id="donut-svg" width="100%" height="100%">
        </svg>
    </div>
    <div id="tooltip-pie" class="tooltip-pie" style="opacity:0;">
        <p><span id="tooltip-value"></span></p>
    </div>
</template>

<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { schemeCategory10 } from 'd3-scale-chromatic';
import { Messages } from '../types';

interface ClusterNumber {
    cluster: string;
    cluster_summary: string;
    model: string;
    
}

export default {
    /*
    props: {
        someProp: {
            type: Array,
            default: () => []  // Provide a default empty array
        }
    },*/
    data() {
        return {
            chartData: [] as ClusterNumber[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: { left: 50, right: 50, top: 50, bottom: 50 } as Margin,
        }
    },
    computed: {
        rerender() {
            return (!isEmpty(this.chartData)) && this.size
        },
    },
    async created() {
        // const rawData = this.someProp;
        const rawData = await d3.csv("../../data/proc/palm-2.csv");
        let parsedData = rawData.map(d => ({
            cluster: d.cluster.toString(),
            model: d.model,
            cluster_summary: d.cluster_summary,
        }) as { cluster: string; cluster_summary: string; model: string });
        console.log(rawData[0]);
        this.chartData = parsedData; 
    },
    methods: {
        onResize() {
            let target = this.$refs.donutContainer as HTMLElement;
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            let donutContainer = d3.select('#donut-svg');

            const radius = Math.min(this.size.width - this.margin.left - this.margin.right,
                this.size.height - this.margin.top - this.margin.bottom) / 2;

            const groupedData = this.chartData.reduce((acc, cur) => {
                const clusterNumber = cur.cluster;
                const clusterSummary = cur.cluster_summary;
                if (acc[clusterNumber]) {
                    acc[clusterNumber].count++;
                } else {
                    acc[clusterNumber] = { count: 1, summary: clusterSummary };
                }
                return acc;
            }, {} as Record<string, { count: number, summary: string }>);

            const uniqueChartData = Object.entries(groupedData).map(([clusterNumber, { count, summary }]) => ({
                cluster: clusterNumber,
                count: count,
                summary: summary
            }));
            
            const sortedData = uniqueChartData.sort((a, b) => b.count - a.count);

            const pie = d3.pie<{ cluster: string; count: number; summary: string }>()
                .value(d => d.count);

            const arcs = pie(sortedData);

            const arc = d3.arc()
                .innerRadius(radius * 0.6)
                .outerRadius(radius);

            const group = donutContainer.append('g')
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height / 2})`);

            const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"];

            const tooltip = d3.select("#tooltip-pie");
            group.selectAll('path')
                .data(arcs)
                .join('path')
                .attr('d', d => arc(d as any) as string)
                // Use the index to select a color from the array
                .attr('fill', (d, i) => colors[i % colors.length])
                .on("mouseover", (event, d) => {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(`Cluster Summary: ${d.data.summary} <br> Message Count: ${d.data.count}`)
                        .style("left", (event.pageX) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                .on("mouseout", () => {
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                }); 

            const arcLabel = d3.arc()
                .innerRadius(radius * 1.1)
                .outerRadius(radius * 1.1);

            // Add labels
            group.selectAll('text')
                .data(arcs)
                .join('text')
                .attr('transform', d => `translate(${arcLabel.centroid(d as any)})`)
                .attr('dy', '0.5em')
                .attr('fill', 'black')
                .attr('text-anchor', 'middle')
                .style('font-size', '0.8rem')
                .text(d => `${d.data.cluster} (${d.data.count})`);

            const title = donutContainer.append('g')
                .append('text')
                .attr('transform', `translate(${this.size.width / 2}, ${this.margin.top / 2})`)
                .attr('dy', '0px')
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .text('Message distribution across Clusters 0-9');
        }
    },
    watch: {
        rerender(newSize) {
            if (!isEmpty(newSize)) {
                d3.select('#donut-svg').selectAll('*').remove()
                this.initChart()
            }
        },
    },
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.onResize()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.onResize)
    }
}
</script>

<style scoped>
.chart-container-donut {
    height: 100%;
}
.tooltip-pie {
    position: absolute;
    text-align: center;
    width: 200px;
    height: 60px;
    padding: 2px;
    font: 12px sans-serif;
    background: lightsteelblue;
    border: 0px;
    border-radius: 8px;
    pointer-events: none;
    overflow-y: scroll;
}

/* Hide the tooltip when not in use */
.tooltip-pie {
    opacity: 0;
}
</style>