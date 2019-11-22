<template>
  <div>

  </div>
</template>

<script>
import { ENGINE_HOST } from "~/settings.js";
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export default {
  async created() {
    this.$store.commit("connection/connect");
  }

}
</script>
