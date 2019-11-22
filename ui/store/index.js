import { ENGINE_URI } from "~/settings.js";
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export const state = () => ({
  socket: null,
})

export const mutations = {
  enter() {
    state.socket = new WebSocket(`${ENGINE_URI}/v1/play`);

    state.socket.onopen = (event) => {

    }

    state.socket.onmessage = (event) => {
      const json = JSON.parse(event.data);
      switch(json.type) {
        case 'authorization-request':
          socket.send(JSON.stringify({
            type: 'authorization-response',
            data: {
              token: WebToken.token,
              character: {
                id: WebToken.payload.data.character.id
              }
            }
          }));
          break;
      }
    }
  }
}
