<template>
  <div>
    <top-nav />
    <connection />
    <nuxt />
  </div>
</template>

<script>
import TopNav from "~/components/TopNav.vue";
import Connection from "~/components/Connection.vue";

export default {
  components: {
    TopNav,
    Connection
  }
}
</script>
