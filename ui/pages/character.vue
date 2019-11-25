<template>
  <div>
    <div v-if="!characters.models.length">
      <div class="ui centered grid">
        <div class="row">
          <h1>New Player?</h1>
        </div>
      </div>
      <create-character />
    </div>
    <div v-else>

    </div>
  </div>
</template>

<script>
import { API_HOST } from "~/settings.js";
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";
import { Collection } from "~/vendor/sugar-data/lib/collection.js";

import CreateCharacter from "~/components/CreateCharacter.vue";

export default {
  data() {
    return {
      characters: new Collection({
        host: API_HOST,
        uri: "v1",
        type: "characters"
      })
    };
  },
  components: {
    CreateCharacter
  },
  async created() {
    if(!WebToken.authenticated) {
      this.$router.push({ name: "login" });
      return null;
    }
    await this.characters.find({
      query: { profile: WebToken.payload.data.id }
    });
    console.log(this.characters.models);
    if(this.characters.errored) {
      for(let error of this.characters.errors) {
        this.$store.commit("message/add", error);
      }
    }
  }
}
</script>
