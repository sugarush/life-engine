<template>
  <div class="ui pointing menu">
    <nuxt-link class="item" :to=" { name: 'character' }">Character</nuxt-link>
    <nuxt-link class="item right" v-if="!WebToken.authenticated" :to="{ name: 'login' }">Login</nuxt-link>
    <nuxt-link class="item right" v-if="WebToken.authenticated" :to="{ name: 'logout' }">Logout</nuxt-link>
  </div>
</template>

<script>
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export default {
  data() {
    return {
      WebToken
    };
  }
}
</script>
