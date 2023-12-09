<script lang="ts">
import Pie from './components/Pie.vue';
import Embeddings from './components/Embeddings.vue';
import Sankey from './components/Sankey.vue';
import Bar from './components/Bar.vue';

export default {
  components: {
    Pie,
    Embeddings,
    Sankey,
    Bar,
  },
  
}

</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
    <h1 style="text-align: center;">ChatViz: Visualization Dashboard for LLM Applications</h1>
    <v-row no-gutters>
      <v-col>
        <Embeddings />
      </v-col>
    </v-row>
    <hr>
    <v-row no-gutters>
      <v-col cols="4">
        <Pie />
      </v-col>
      <v-col cols="8">
        <Sankey />
      </v-col>
    </v-row>
  </v-container>
    
</template>

<style scoped>
#main-container{
  height: 100%;
}
</style>