<template>
  <form class="ui form">
    <h2 class="ui dividing header">Character Name</h2>
    <div class="field">
      <label>Name</label>
      <div class="two fields">
        <div class="field">
          <input type="text" v-model="character.attributes.name.first" placeholder="First Name">
        </div>
        <div class="field">
          <input type="text" v-model="character.attributes.name.last" placeholder="Last Name">
        </div>
      </div>
    </div>
    <h2 class="ui dividing header">Profession</h2>
  </form>
</template>

<script>
import { API_HOST } from "~/settings.js";

import { Model } from "~/vendor/sugar-data/lib/model.js";

export default {
  data() {
    return {
      character: new Model({
        host: API_HOST,
        uri: "v1",
        type: "characters",
        attributes: {
          name: { }
        }
      })
    };
  }
}
</script>
