import { ENGINE_HOST } from "~/settings.js";
import WebToken from "~/vendor/sugar-data/lib/webtoken.js";

export const state = () => ({
  socket: null,
})

export const mutations = {
  connect(state) {
    state.socket = new WebSocket(`${ENGINE_HOST}/v1/play`);

    state.socket.onmessage = (event) => {
      const json = JSON.parse(event.data);
      switch(json.type) {
        case 'authorization-request':
          state.socket.send(JSON.stringify({
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
