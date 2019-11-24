<template>

</template>

<script>
import { API_HOST } from "~/settings.js";
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export default {
  created() {
    this.interval = setInterval(async () => {
      if(WebToken.authenticated) {
        await WebToken.refresh(`${API_HOST}/v1/authentication`);
        if(WebToken.errored) {
          for(let error of WebToken.errors) {
            this.$store.commit("message/add", error);
          }
        }
      }
    }, 240000);
  },
  destroyed() {
    clearInterval(this.interval);
  }
}
</script>
