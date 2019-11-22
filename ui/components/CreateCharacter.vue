<template>

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
        type: "characters"
      })
    };
  }
}
</script>
