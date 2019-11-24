<template>
  <div>
    <div class="ui message" v-for="message in $store.state.message.messages">
      <div class="header">
        {{ message.title }}
      </div>
      <p>{{ message.detail }}</p>
    </div>
  </div>
</template>

<script>
export default {
  created() {
    this.interval = setInterval(() => {
      this.$store.commit('message/expire');
    }, 1000);
  },
  destroyed() {
    clearInterval(this.interval);
  }
}
</script>

<style lang="scss" scoped>
div {
  margin: 25px;
}
</style>
