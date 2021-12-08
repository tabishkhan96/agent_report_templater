import {createStore} from "vuex";

const store = createStore({
  state () {
    return {
      report: {
        order: '',
        number: '',
        place_of_inspection: '',
        inspection_date: '',
        surveyor: '',
        transport_units: []
      },
      transportUnitModel: {
        number: '',
        supplier: '',
        cargo: [],
        card: [],
        cultivar: [],
        units: [],
        invoice: '',
        date: '',
        calibre: [],
        temperature: {},
        pallets: 0,
        damaged_pallets: 0,
        boxes: 0,
        damaged_boxes: 0,
        cargo_damage: 0,
        empty_boxes: 0,
        not_full_boxes: 0,
        photos: []
      },
      temperatureDataModel: {
        recommended: 0.0,
        pulp: {},
        violations_affect: '1',
        thermographs: []
      },
      pulpDataModel: {
        min: 0.0,
        max: 0.0
      },
      thermographDataModel: {
        number: '',
        graph: null,
        worked: '0',
        min: 0.0,
        max: 0.0
      },
      photoModel: {
        id: 0,
        file: '',
        rotation: 0
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
        number: '',
        place_of_inspection: '',
        inspection_date: '',
        surveyor: '',
        transport_units: []
      };
    },
  }
});

export { store };
