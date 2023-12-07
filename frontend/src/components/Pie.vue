<template>
    <div class="chart-container-donut" ref="donutContainer">
        <svg id="donut-svg" width="100%" height="100%">
        </svg>
    </div>
</template>

<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { schemeCategory10 } from 'd3-scale-chromatic';

interface ClusterNumber {
    cluster: string;
    model: string;
    
}

export default {
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
        const rawData = await d3.csv("../../data/palm-2.csv");
        let parsedData = rawData.map(d => ({
            cluster: (d.cluster).toString(),
            model: d.model,
        }));
        console.log(rawData[0]);
        this.chartData = parsedData.filter((d) => d.model == "palm-2");
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

            // Count the occurrences of each job title
            const groupedData = this.chartData.reduce((acc, cur) => {
                const clusterNumber = cur.cluster || "Other"; // Use a default value "Other" if cluster is undefined
                if (acc[clusterNumber]) {
                    acc[clusterNumber]++;
                } else {
                    acc[clusterNumber] = 1;
                }
                return acc;
            }, {} as Record<string, number>);

            const uniqueChartData = Object.entries(groupedData).map(([clusterNumber, count]) => ({
                cluster: clusterNumber,
                count: count
            }));

            const sortedData = uniqueChartData.sort((a, b) => b.count - a.count);

            const topJobs = sortedData.slice(0, 8);

            const otherCount = sortedData.slice(8).reduce((acc, cur) => acc + cur.count, 0);

            const updatedChartData = [...topJobs, { cluster: "Other", count: otherCount }];

            const pie = d3.pie<{ cluster: string; count: number }>()
                .value(d => d.count);

            const arcs = pie(updatedChartData);

            const arc = d3.arc()
                .innerRadius(radius * 0.6)
                .outerRadius(radius);

            const group = donutContainer.append('g')
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height / 2})`);

            const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"];

            group.selectAll('path')
                .data(arcs)
                .join('path')
                .attr('d', d => arc(d as any) as string)
                // Use the index to select a color from the array
                .attr('fill', (d, i) => colors[i % colors.length]);
            
            /* use predefined colors above for each cluster 
            const colorScale = d3.scaleOrdinal()
                .domain(updatedChartData.map(d => d.cluster))
                .range(schemeCategory10);

            group.selectAll('path')
                .data(arcs)
                .join('path')
                .attr('d', d => arc(d as any) as string)
                .attr('fill', (d, i) => colorScale(d.data.cluster) as string);
            */

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
</style>