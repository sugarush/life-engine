<template>
  <div class='ui container'>
    <top-nav />
    <message />
    <nuxt />
    <token-refresh />
  </div>
</template>

<script>
import TopNav from "~/components/TopNav.vue";
import Message from "~/components/Message.vue";
import TokenRefresh from "~/components/TokenRefresh.vue";

export default {
  components: {
    TopNav,
    Message,
    TokenRefresh
  }
}
</script>
