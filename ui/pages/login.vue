<template>
  <div class="ui two column centered grid">
    <div class="row">
      <h1>Login</h1>
    </div>
    <div class="row">
      <div class='ui input'>
        <input type="text" @keypress.enter='login' v-model="username"></input>
      </div>
    </div>
    <div class="row">
      <div class='ui input'>
        <input type="password" @keypress.enter='login' v-model="password"></input>
      </div>
    </div>
    <button class='ui button' @click='login'>Login</button>
  </div>
</template>

<script>
import { API_HOST } from "~/settings.js";
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export default {
  data() {
    return {
      WebToken,
      username: "",
      password: ""
    }
  },
  methods: {
    async login() {
      await WebToken.authenticate(`${API_HOST}/v1/authentication`, {
        'data': {
          'attributes': {
            'username': this.username,
            'password': this.password
          }
        }
      });
      if(WebToken.errored) {
        for(let error of WebToken.errors) {
          this.$store.commit('message/add', error);
        }
      } else {
        this.$router.push({ name: 'character' });
      }
    }
  }
}
</script>
