const socket = new WebSocket('ws://localhost:8000/v1/play');

socket.onopen = (event) => {

}

socket.onmessage = (event) => {
  const json = JSON.parse(event.data);
  switch(json.type) {
    case 'authorization-request':
      
      break;
  }
}

export const state = () => ({
  socket: socket,
  stats: { }
})

export const mutations = {
  set_stats(value) {
    state.stats = value
  }
}
