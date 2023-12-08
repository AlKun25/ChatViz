<script lang="ts">
import * as d3 from "d3";
import Pie from './components/Pie.vue';
import Embeddings from './components/Embeddings.vue';
import Sankey from './components/Sankey.vue';
import Bar from './components/Bar.vue';
import { Messages } from './types';

export default {
  data() {
    return {
      parentData: [] as Messages[],
    };
  },
  components: {
    Pie,
    Embeddings,
    Sankey,
    Bar,
    /*
    ExampleWithLegend,
    ExampleWithInteractions*/
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

        this.parentData = parsedData.filter((d) => d.model == "palm-2");
    },

  
}
  /*
  methods: {
    handleChildEvent(value) {
      // do something when event is emitted
      
    }
  }*/
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
    <h1 style="text-align: center;">ChatViz: Visualization Dashboard for LLM Applications</h1>
    <v-row no-gutters>
      <v-col>
        <Embeddings :someProp="parentData" />
      </v-col>
    </v-row>
    <hr>
    <v-row no-gutters>
      <v-col cols="4">
        <Pie :someProp="parentData" />
      </v-col>
      <v-col cols="8">
        <Sankey :someProp="parentData" />
      </v-col>
    </v-row>
  </v-container>
    
</template>

<style scoped>
#main-container{
  height: 100%;
}
</style>