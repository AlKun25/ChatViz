<template>
    <div class="chart-container-embeddings" id="chart-container-embeddings" ref="embeddingContain">
    </div>
</template>

<script lang="ts">
import * as THREE from 'three';
import { NormalBufferAttributes } from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import * as d3 from "d3";
import { isEmpty, debounce } from 'lodash';
import { ComponentSize, Margin } from '../types';
import { useEventEmitter } from '../emitter';

const emitter = useEventEmitter();


interface Messages {
    message_id: string;
    embedding: string;
    cluster: string;
    cluster_summary: string;
    content: string;
    openai_moderation: string;
    toxicity: string;
    role: string;
    turn: number;
    model: string;
    
}

export default {
    data() {
        return {
            chartData: [] as Messages[],
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
            renderer.setSize(window.innerWidth, window.innerHeight * 0.8);
            renderer.domElement.style.height = '80%';
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
                }
            }
            document.addEventListener('mousedown', onDocumentMouseDown as EventListener, false);

            function showDataForPoint(data: Messages) {
                // show text analysis for the point
                // this function gets called when user clicks on a point
                const summary = data.cluster_summary;
                console.log("summary: ", summary);
                
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
