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
import { API_URI } from "~/settings.js";
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
      await WebToken.authenticate(`${API_URI}/v1/authentication`, {
        'data': {
          'attributes': {
            'username': this.username,
            'password': this.password
          }
        }
      });
      if(!WebToken.errored) {
        this.$router.push({ name: 'character' });
      }
    }
  }
}
</script>
