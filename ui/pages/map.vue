<template>
  <div>
    <div id="map"></div>
    <span>[ {{ click.lng }}, {{ click.lat }} ]</span>
  </div>
</template>

<script>
import { API_HOST } from "~/settings.js";
import { jsonapi } from "~/vendor/sugar-data/lib/request.js";
import { Model } from "~/vendor/sugar-data/lib/model.js";

export default {
  data() {
    return {
      characters: [ ],
      click: { }
    }
  },
  async mounted() {
    let json = await jsonapi(`${API_HOST}/v1/scan/-84.54194682144171/42.41184078897055/1000/km`);
    if(json.errors) {
      for(let error of json.errors) {
        this.$store.commit('message/add', error);
      }
    } else {
      mapboxgl.accessToken = 'pk.eyJ1IjoibHVjaWZlcnNlYXJzIiwiYSI6ImNrM2NndHk1NDBka2IzYm9rdmd1eGcyZGsifQ.kzhZ51nIK3VQTB_FYFlF8Q';
      var map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/satellite-streets-v10?optimize=true',
        center: [ -84.54194682144171, 42.41184078897055 ],
        zoom: 17
      });
      map.on('click', (event) => {
        this.click = event.lngLat;
      });
      for(let oid of json.data.attributes.characters) {
        json = await jsonapi(`${API_HOST}/v1/characters/${oid}`);
        var marker = new mapboxgl.Marker()
          .setLngLat(json.data.attributes.location.coordinates)
          .addTo(map);
      }
    }
  }
}
</script>

<style lang="scss" scoped>
#map {
  height: 800px;
}
</style>
