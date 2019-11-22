<template>
  <div class="ui two column centered grid">
    <div class="row">
      <h1>Logout</h1>
    </div>
    <div class="row">
      <button class="ui button" @click='logout'>Logout</button>
    </div>
  </div>
</template>

<script>
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export default {
  methods: {
    logout() {
      WebToken.deauthenticate();
      this.$router.push({ name: "login" });
    }
  }
}
</script>
