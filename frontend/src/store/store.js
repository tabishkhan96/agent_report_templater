import {createStore} from "vuex";

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
        not_full_boxes: 0
      },
      temperatureDataModel: {
        recommended: 0.0,
        pulp: {},
        thermographs: []
      },
      pulpDataModel: {
        min: 0.0,
        max: 0.0
      },
      thermographDataModel: {
        graph: null,
        worked: '',
        min: 0.0,
        max: 0.0
      },
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

export { store };
