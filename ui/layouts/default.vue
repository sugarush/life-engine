<template>
  <div class='ui container'>
    <top-nav />
    <message />
    <nuxt />
  </div>
</template>

<script>
import TopNav from "~/components/TopNav.vue";
import Message from "~/components/Message.vue";

export default {
  components: {
    TopNav,
    Message
  }
}
</script>
