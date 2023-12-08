<template>
    <v-switch @click="toggleColor" label="Show Toxicity"></v-switch>
    <div class="chart-container-embeddings" id="chart-container-embeddings" ref="embeddingContain">
        <div id="popup" class="popup" style="opacity:0;">
            <!--div class="row"><button id="close-button" @click="hidePopup">[close]</button></div-->
            <div class="row"><h3>Message Details</h3><div id="popup-content"></div></div>
            <v-row style="height: 300px">
                <v-col cols="5" style="height: 250px">
                    <Bar />
                </v-col>
                <v-col cols="7" style="height: 250px">
                    <Radar />
                </v-col>
            </v-row>
        </div>
        <div id="legends">
        </div>
    </div>
    
    <div id="overlay">
      <div class="loader">
      </div>
    </div>
</template>

<script lang="ts">
import * as THREE from 'three';
import { NormalBufferAttributes } from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import * as d3 from "d3";
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin, Messages } from '../types';
import { useEventEmitter } from '../emitter';
import { state } from '../state';
import Bar from './Bar.vue';
import Radar from './Radar.vue';

const emitter = useEventEmitter();


export default {
    data() {
        return {
            chartData: [] as Messages[],
            size: { width: 0, height: 0 } as ComponentSize,
            margin: { left: 50, right: 50, top: 50, bottom: 50 } as Margin,
            showToxicity: false,
            selectedMessage: [] as Messages[],
        }
    },
    components: {
        Bar,
        Radar,
    },
    computed: {
        rerender() {
            return (!isEmpty(this.chartData)) && this.size
        },
    },
    async created() {
        const rawData = await d3.csv("../../data/proc/palm-2.csv");
        let parsedData = rawData.map(d => ({
            message_id: d.message_id,
            embedding: d.vector,
            cluster: (d.cluster).toString(),
            cluster_summary: d.cluster_summary,
            content: d.content,
            openai_moderation: d.openai_moderation,
            toxicity: d.toxicity,
            role: d.role,
            turn: parseInt(d.turn),
            model: d.model,
        }));
        console.log(rawData[0]);
        this.chartData = parsedData.filter((d) => d.model == "palm-2");
    },
    methods: {
        showLoading: function (seconds: number) {
            const overlay = document.getElementById("overlay");
            if (overlay) {
                overlay.style.display = "block";
                setTimeout(function () {
                    overlay.style.display = "none";
                }, seconds * 1000);
            } 
        },
        hideLoading: function () {
            const overlay = document.getElementById("overlay");
            if (overlay) {
                overlay.style.display = "none";
            }
        },
        toggleColor() {
            this.showLoading(10);
            this.showToxicity = !this.showToxicity;
            d3.select('#chart-container-embeddings').selectAll('*').remove();
            this.initChart();
        },
        hidePopup() {
            const popup = d3.select("#popup");
            popup.transition()
                    .duration(500)
                    .style("opacity", 0);
        },
        onResize() {
            let target = this.$refs.donutContainer as HTMLElement;
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            let object3DToDataMap = new Map();
            let that = this;
            
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera( 75, window.innerWidth / window.innerHeight, 0.1, 1000 );
            camera.fov = 120;
            camera.updateProjectionMatrix();

            const renderer = new THREE.WebGLRenderer();
            renderer.setSize( window.innerWidth, window.innerHeight );
            renderer.setClearColor(0xFFFFFF, 1);
            renderer.setSize(window.innerWidth, window.innerHeight * 0.7);
            renderer.domElement.style.height = '70%';
            renderer.domElement.style.width = '100%';

            let embedding_div = document.getElementById("chart-container-embeddings");
            if (embedding_div !== null) {
                embedding_div.appendChild(renderer.domElement);
            }
            const controls = new OrbitControls(camera, renderer.domElement);

            // Adjust control settings
            controls.enableDamping = true;
            controls.dampingFactor = 0.25;
            controls.enableZoom = true;
            controls.enablePan = true;

            // colors for each cluster category
            const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"];
            
            let points = new THREE.Group();
            // create a Points object for each entry in chartData
            this.chartData.forEach(d => {
                let coords = JSON.parse(d.embedding);
                let x = coords[0];  
                let y = coords[1];
                let z = coords[2];
                const vertices = new Float32Array([ x, y, z ]);
                let geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
                let color = colors[parseInt(d.cluster)];
                if (this.showToxicity) {
                    if (d.toxicity == "True") {
                        color = "#DC3220";
                    } else {
                        color = "#005AB5";
                    }
                }
                const pointMaterial = new THREE.PointsMaterial({ color: color, size: 0.2 });
                const point = new THREE.Points(geometry, pointMaterial);
                point.userData = d;
                object3DToDataMap.set(point, d);  
                points.add(point);
            });
            
            let selectedPoint: THREE.Points | null = null;
            let draggableObjects = [points]; 
            const raycaster = new THREE.Raycaster();
            const pointerVector = new THREE.Vector2();
            scene.add(points);

            function onDocumentMouseDown(event: PointerEvent) {
                event.preventDefault();

                pointerVector.x = (event.clientX / window.innerWidth) * 2 - 1;
                pointerVector.y = -(event.clientY / window.innerHeight) * 2 + 1;

                raycaster.setFromCamera(pointerVector, camera);
                const intersects = raycaster.intersectObjects(draggableObjects, true);

                if (intersects.length > 0) {
                    const intersect = intersects[0];
                    
                    selectedPoint = intersect.object as THREE.Points<THREE.BufferGeometry<NormalBufferAttributes>, THREE.Material | THREE.Material[]>;
                    const data = object3DToDataMap.get(intersect.object);  // Retrieve the mapping.

                    if (data) {
                        showDataForPoint(data);
                    } 
                } else {
                    that.hidePopup();
                }
            }
            document.addEventListener('mousedown', onDocumentMouseDown as EventListener, false);
            const selections = state.selections;

            function showDataForPoint(data: Messages) {
                Object.entries(data).forEach(([key, value]) => {
                    selections.set(key, value);
                });
                emitter.$emit('update-chart', data);
                // show text analysis for the point
                // this function gets called when user clicks on a point
                const summary = data.cluster_summary;
                console.log("summary: ", summary);
                // sankey, text analysis, etc.
                const popup = d3.select("#popup");
                const popupcontent = d3.select("#popup-content");
                popup.transition()
                        .duration(200)
                        .style("opacity", .9);
                popupcontent.html(`<b>Message:</b> ${data.content} <br><b>Cluster ${data.cluster}:</b> ${data.cluster_summary} <br><b>Role:</b> ${data.role}<br><b>Toxicity:</b> ${data.toxicity}<br>`);
                
            }
            
            // how far away the camera is from the points on the z-axis
            camera.position.z = 35;

            function animate() {
                requestAnimationFrame( animate );

                // points.rotation.x += 0.01;
                // points.rotation.y += 0.01;

                controls.update();
                renderer.render( scene, camera );
            }

            animate();
            this.hideLoading();

            d3.select("#legends").selectAll('*').remove(); // Clear existing legend entries if any.
            const clusterNames = ["Cluster 0: Shocking aspect of NAME_1's past?", 
            "Cluster 1: Thesis on Network-Level Brute Force Detection", 
            "Cluster 2: Device for raising/lowering boats in waterways.", 
            "Cluster 3: Topic's controversy explained.", 
            "Cluster 4: Multiplication by chunking steps.", 
            "Cluster 5: Locate cheap, used RTX4090 computer.", 
            "Cluster 6: Unable to assist, provide feedback if erroneous.", 
            "Cluster 7: NAME_1 and NAME_3 found an empty vault.", 
            "Cluster 8: Paper on attention-based neural network model.", 
            "Cluster 9: Fix non-existent error."];
            const legendContainer = d3.select("#legends");

            legendContainer.append('text')
            .text('Cluster Topic Summary')
            .attr('x', 10)
            .attr('y', 8)
            .style('font-weight', 'bold')
            .style('text-anchor', 'start');
            
            // Bind the data to the legend container, creating one `.legend-entry` div per cluster name
            let legendEntry = legendContainer.selectAll('.legend-entry')
                .data(clusterNames)
                .enter()
                .append('div')
                .attr('class', 'legend-entry');

            

            // Append a color box to each legend entry
            legendEntry.append('div')
                .attr('class', 'legend-color-box')
                .attr('fill', colors)
                .attr('x', 90)
                .attr('y', 40)
                .attr('z-index', 1000000000000)
                .style('background-color', (d, i) => colors[i])
                .style('width', '15px')
                .style('height', '15px');


            // Append a text label to each legend entry
            legendEntry.append('div')
                .attr('class', 'legend-text')
                .text(d => d)
                .style('font-size', '10px');

            
            
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
.loader {
  border: 16px solid #f3f3f3; /* Light grey */
  border-top: 16px solid #10a37f;
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
  position: relative;
  top: 45%;
  left: 45%;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
#overlay {
  position: fixed; /* Sit on top of the page content */
  width: 100%; /* Full width (cover the whole page) */
  height: 100%; /* Full height (cover the whole page) */
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5); /* Black background with opacity */
  z-index: 2; /* Specify a stack order in case you're using a different order for other elements */
  cursor: pointer; /* Add a pointer on hover */
}
.popup {
    position: absolute;
    text-align: center;
    width: 700px;
    height: 450px;
    padding: 2px;
    font: 12px sans-serif;
    background: lightsteelblue;
    border: 0px;
    border-radius: 8px;
    pointer-events: none;
    opacity: 0;
    overflow: scroll;
}
#close-button {
    position: absolute;
    right: 2px;
    cursor: pointer;
    z-index:10;
}
#legends {
  width: 200px;
  position: absolute;
  top: 50px; /* Adjust as needed */
  right: 20px; /* Adjust as needed */
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
  z-index: 100; /* Make sure the legend is above the Three.js canvas */
}

.legend-entry {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.legend-color-box {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  border: 1px solid #000;
}

.legend-text {
  font-size: 10px;
  color: #333;
}
</style>