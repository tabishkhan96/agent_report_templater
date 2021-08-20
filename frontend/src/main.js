import { createApp } from 'vue';
import { createStore } from 'vuex';
import App from './App.vue';

const store = createStore({
  state () {
    return {
      report: {
        order: '',
        report_number: '',
        place_of_inspection: '',
        inspection_date: '',
        vessel: '',
        transport_units: []
      },
      transportUnit: {
          number: '',
          supplier: '',
          cargo: [],
          card: [],
          cultivar: [],
          units: [],
          invoice: '',
          date: '',
          calibre: [],
          temperature: {
            recommended: 0.0,
            pulp: {
              min: 0.0,
              max: 0.0
            },
            thermographs_number: 0,
            thermographs: [{
              graph: null,
              malfunction: '',
              min: 0.0,
              max: 0.0
            }]
          },
          pallets: 0,
          damaged_pallets: 0,
          boxes: 0,
          damaged_boxes: 0,
          cargo_damage: 0,
          empty_boxes: 0,
          not_full_boxes: 0
        }
    };
  },
  mutations: {
    setReport (state, obj) {
      state.report = obj;
    },
    dropReport (state) {
      state.report = {
        order: '',
        report_number: '',
        place_of_inspection: '',
        inspection_date: '',
        vessel: '',
        transport_units: []
      };
    },
  }
});

const app = createApp(App);
app.mount('#app');
app.use(store);
