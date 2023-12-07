<template>
    <div class="chart-container-radar" ref="radarContainer">
        <svg id="radar-svg" width="100%" height="100%">
        </svg>
    </div>
</template>

<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { schemeCategory10 } from 'd3-scale-chromatic';

interface Toxicity {
    hate: number;
    harassment: number;
    self_harm: number;
    sexual: number;
    violence: number;
}

export default {
    data() {
        return {
            chartData: [] as Toxicity[],
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
            message_id: d.message_id,
            openai_moderation: d.openai_moderation,
        }));
        console.log(rawData[0]);
    },
    methods: {
        onResize() {
            let target = this.$refs.donutContainer as HTMLElement;
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            d3.select('#radar-svg').selectAll('*').remove()
            let svgWidth = this.size.width;
            let svgHeight = this.size.height;
            let svg = d3.select("#radar-svg")
                .attr("width", svgWidth)
                .attr("height", svgHeight);

            let centerX = svgWidth / 2 - 75;
            let centerY = svgHeight / 2;
            centerX = Math.round(centerX * 10) / 10;
            centerY = Math.round(centerY * 10) / 10;

            let circleRadius = Math.min(svgWidth, svgHeight) / 3.75;

            let elements = Object.keys(this.chartData);
            let numElements = elements.length;
            let angleOffset = (2 * Math.PI) / numElements;

            let colors = [
                "rgba(0, 128, 0, 0.3)",
                "rgba(255, 0, 0, 0.3)",
                "rgba(0, 0, 255, 0.3)",
                "rgba(255, 255, 0, 0.3)",
                "rgba(0, 255, 255, 0.3)",
                "rgba(255, 0, 255, 0.3)",
                "rgba(192, 192, 192, 0.3)",
                "rgba(128, 128, 0, 0.3)",
                "rgba(128, 0, 128, 0.3)",
                "rgba(0, 128, 128, 0.3)",
                "rgba(128, 128, 128, 0.3)",
                "rgba(255, 165, 0, 0.3)",
                "rgba(255, 192, 203, 0.3)",
                "rgba(255, 228, 225, 0.3)",
                "rgba(255, 255, 224, 0.3)",
                "rgba(51, 161, 201, 0.3)",
                "rgba(0, 138, 184, 0.3)",
                "rgba(0, 110, 145, 0.3)",
                "rgba(0, 82, 109, 0.3)",
                "rgba(0, 55, 73, 0.3)"
            ];

            svg.append("circle")
                .attr("cx", centerX)
                .attr("cy", centerY)
                .attr("r", circleRadius)
                .attr("stroke", "black")
                .attr("fill", "none");

            for (let i = 0; i < numElements; i++) {
                let angle = i * angleOffset;
                let x1 = centerX;
                let y1 = centerY;
                let x2 = centerX + circleRadius * Math.cos(angle);
                let y2 = centerY + circleRadius * Math.sin(angle);
                x2 = Math.round(x2 * 10) / 10;
                y2 = Math.round(y2 * 10) / 10;

                svg.append("line")
                    .attr("x1", x1)
                    .attr("y1", y1)
                    .attr("x2", x2)
                    .attr("y2", y2)
                    .attr("stroke", "gray");

                svg.append("text")
                    .attr("x", x2)
                    .attr("y", y2)
                    .attr("dx", x2 == centerX ? 20 : (x2 > centerX ? 10 : -10))
                    .attr("dy", y2 == centerY ? 10 : (y2 < centerY ? -10 : 20))
                    .text(function () {
                        return elements[i].split("_").map(function (word) {
                            return word.charAt(0).toUpperCase() + word.slice(1);
                        }).join(" ");
                    })
                    .attr("text-anchor", x2 > centerX ? "start" : "end")
                    .attr("alignment-baseline", "middle")
                    .attr("fill", "black");

            }

            let colorIndex = 0;

            let rectangle = svg.append("rect")
                .attr("x", 0)
                .attr("y", 40)
                .attr("width", 170)
                .attr("height", 120)
                .attr("fill", "transparent")
                .attr("stroke", "transparent")
                .attr("rx", 10)
            let keyText = svg.append("text")
                .attr("x", 100)
                .attr("y", 40)
                .text("")
                .attr("text-anchor", "end")
                .attr("font-size", "10px");



            for (let key in this.chartData) {
                if (this.chartData.hasOwnProperty(key)) {
                    let elementData = this.chartData[key];
                    console.log(elementData);
                    let elementValues = Object.values(elementData);
                    console.log(elementValues);

                    let numElements = elementValues.length;
                    let angleOffset = (2 * Math.PI) / numElements;

                    let labelRadius = circleRadius + 26;
                    let elementPositions = [];

                    for (let i = 0; i < numElements; i++) {
                        let angle = i * angleOffset;
                        let x = centerX + labelRadius * Math.cos(angle);
                        let y = centerY + labelRadius * Math.sin(angle);
                        elementPositions.push({ x: x, y: y });
                    }

                    let polygonVertices = elementPositions.map(function (pos, i) {
                        let scaledValue = 1 + (elementValues[i] / 100) * 100;
                        return [
                            centerX + (circleRadius * scaledValue / 130) * Math.cos(i * angleOffset),
                            centerY + (circleRadius * scaledValue / 130) * Math.sin(i * angleOffset)
                        ];
                    });

                    polygonVertices.push(polygonVertices[0]);

                    let color = colors[colorIndex % colors.length];
                    colorIndex++;

                    svg.append("path")
                        .datum(polygonVertices)
                        .attr("d", d3.line())
                        .attr("fill", color)
                        .attr("stroke", color)
                        .attr("class", "polygon")
                        .attr("data-key", key);
                }
            }

            let legendX = svgWidth - 150;
            let legendY = 50;
            let legendSpacing = 25;

            let legend = svg.append("g")
                .attr("class", "legend")
                .attr("transform", "translate(" + legendX + "," + legendY + ")");

            let legendLabels = legend.selectAll(".legend-label")
                .data(Object.keys(this.chartData))
                .enter().append("g")
                .attr("class", "legend-label")
                .attr("data-key", function (d) {
                    return d;
                })
                .attr("transform", function (d, i) {
                    return "translate(0," + i * legendSpacing + ")";
                });

            legendLabels.append("rect")
                .attr("x", 0)
                .attr("width", 20)
                .attr("height", 20)
                .attr("fill", function (d, i) {
                    return colors[i % colors.length];
                });

            legendLabels.append("text")
                .attr("x", 30)
                .attr("y", 10)
                .attr("dy", "0.35em")
                .text(function (d) {
                    return d;
                })
                .attr("fill", "black");

            svg.append("text")
                .attr("x", svgWidth / 2)
                .attr("y", 30)
                .attr("text-anchor", "middle")
                .attr("font-size", "24px")
                .attr("font-weight", "bold")
                .text("Stat Spread Per Pokémon Type");

            // addListener(svg, data, keyText, ".polygon");
            // addListener(svg, data, keyText, ".legend-label");
        },
    },
};
</script>




<style scoped>
.chart-container-radar {
    height: 100%;
}
</style>