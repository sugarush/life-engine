<template>
  <form class="ui form">
    <h2 class="ui dividing header">Name</h2>
    <div class="two fields">
      <div class="field">
        <label>First Name</label>
        <input type="text" v-model="name.first" placeholder="First Name"></input>
      </div>
      <div class="field">
        <label>Last Name</label>
        <input type="text" v-model="name.last" placeholder="Last Name"></input>
      </div>
    </div>
    <h2 class="ui dividing header">About</h2>
    <div class="six fields">
      <div class="field">
        <label>Race</label>
        <select class="ui fluid search dropdown" v-model="race">
          <option value="">Select a race</option>
          <option v-for="(race, name) in races" :value="name">{{ name }}</option>
        </select>
      </div>
      <div class="field">
        <label>Profession</label>
        <select class="ui fluid search dropdown" v-model="profession">
          <option value="">Select a Profession</option>
          <option v-for="(profession, name) in professions" :value="name">{{ name }}</option>
        </select>
      </div>
    </div>
    <div class="fields">
      <div class="eight wide field">
        <h2 class="ui dividing header">Attributes</h2>
        <div class="six fields">
          <div class="field disabled">
            <label>Strength</label>
            <input type="text" v-model="attributes.strength"></input>
          </div>
          <div class="field disabled">
            <label>Dexterity</label>
            <input type="text" v-model="attributes.dexterity"></input>
          </div>
          <div class="field disabled">
            <label>Constitution</label>
            <input type="text" v-model="attributes.constitution"></input>
          </div>
          <div class="field disabled">
            <label>Intelligence</label>
            <input type="text" v-model="attributes.intelligence"></input>
          </div>
          <div class="field disabled">
            <label>Wisdom</label>
            <input type="text" v-model="attributes.wisdom"></input>
          </div>
          <div class="field disabled">
            <label>Charisma</label>
            <input type="text" v-model="attributes.charisma"></input>
          </div>
        </div>
      </div>
      <div class="eight wide field">
        <h2 class="ui dividing header">Resistances</h2>
        <div class="six fields">
          <div class="field disabled">
            <label>Fire</label>
            <input type="text" v-model="resistances.fire"></input>
          </div>
          <div class="field disabled">
            <label>Frost</label>
            <input type="text" v-model="resistances.frost"></input>
          </div>
          <div class="field disabled">
            <label>Poison</label>
            <input type="text" v-model="resistances.poison"></input>
          </div>
          <div class="field disabled">
            <label>Shadow</label>
            <input type="text" v-model="resistances.shadow"></input>
          </div>
          <div class="field disabled">
            <label>Magic</label>
            <input type="text" v-model="resistances.magic"></input>
          </div>
          <div class="field disabled">
            <label>Holy</label>
            <input type="text" v-model="resistances.holy"></input>
          </div>
        </div>
      </div>
    </div>
    <h2 class="ui dividing header">Finalize</h2>
    <button class="ui green button" @click.prevent="create">Create</button>
  </form>
</template>

<script>
import { API_HOST } from "~/settings.js";

import WebToken from "~/vendor/sugar-data/lib/webtoken.js";
import { jsonapi } from "~/vendor/sugar-data/lib/request.js";
import { Model } from "~/vendor/sugar-data/lib/model.js";

export default {
  data() {
    return {
      attributes: { },
      resistances: { },
      professions: { },
      races: { },
      profession: "",
      race: "",
      name: {
        first: "",
        last: "",
      }
    }
  },
  methods: {
    async create() {
      const json = await jsonapi(`${API_HOST}/v1/create`, {
        method: "POST",
        body: {
          data: {
            attributes: {
              name: this.name,
              race: this.race,
              profession: this.profession
            }
          }
        }
      });
      if(json.errors) {
        for(let error of json.errors) {
          this.$store.commit('message/add', error);
        }
      }
    }
  },
  watch: {
    race(value) {
      this.attributes = this.races[value].attributes;
    },
    profession(value) {
      this.resistances = this.professions[value].resistances
    }
  },
  async mounted() {
    let json = await jsonapi(`${API_HOST}/v1/professions`);
    _.assignIn(this.professions, json.data.attributes);
    json = await jsonapi(`${API_HOST}/v1/races`)
    _.assignIn(this.races, json.data.attributes)
    this.$forceUpdate();
    $('.dropdown', this.$el).dropdown();
  }
}
</script>
