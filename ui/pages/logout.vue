<template>
  <div class="ui two column centered grid">
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
    }
  }
}
</script>
