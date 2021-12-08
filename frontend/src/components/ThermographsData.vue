<template>
  <div class="container">
    <div class="row">
      <div>
        <br>
        <br>
        <form @submit.prevent="continueReport">
          <fieldset :disabled="!editable">
            <table class="table table-hover">
              <thead>
                <tr class="d-flex">
                  <th v-for="key in tableHeadersList"
                      :key="key"
                      scope="col"
                      class="col-2">
                    {{ key }}&nbsp;
                  </th>
                  <th class="col-2"></th>
                </tr>
              </thead>
              <tbody>
                <tr
                    v-for="unit in report.transport_units"
                    :key="unit.number"
                    class="d-flex"
                >
                  <td class="col-2"><b>{{ unit.number }}</b></td>
                  <td class="col-2"><input required v-model.lazy="unit.temperature.recommended" type="number" step="0.1"></td>
                  <td class="col-2"><input required v-model.lazy="unit.temperature.pulp.min" type="number" step="0.1" :max="unit.temperature.pulp.max"></td>
                  <td class="col-2"><input required v-model.lazy="unit.temperature.pulp.max" type="number" step="0.1" :min="unit.temperature.pulp.min"></td>
                  <td class="col-2">
                    <select required @change="createThermographsList(unit, $event.target.value)">
                      <option value="0">0</option>
                      <option value="1">1</option>
                      <option value="2">2</option>
                    </select>
                  </td>
                  <td class="col-2">
                    <ul>
                      <li v-for="(thermograph, index) in unit.temperature.thermographs" :key="index">
                        {{ index+1 }} термограф: <select required v-model.lazy="thermograph.worked">
                          <option value="1">Работал</option>
                          <option value="2">Не работал</option>
                          <option value="3">Работал некорректно</option>
                        </select>
                      </li>
                    </ul>
                  </td>
                </tr>
              </tbody>
            </table>
            <table class="table table-hover">
              <tbody>
                <tr
                    v-for="unit in report.transport_units"
                    :key="unit.number"
                    class="d-flex"
                >
                  <td v-if="unit.temperature.thermographs.length"><b>{{unit.number}}</b></td>
                  <td>
                    <table class="table table-hover">
                      <tbody>
                        <tr v-for="(thermograph, index) in unit.temperature.thermographs" :key="index" class="d-flex">
                          <td>{{index+1}}</td>
                          <td class="col-2">
                            <label> Номер датчика: <input required type="text" v-model.lazy="thermograph.number"></label>
                          </td>
                          <td class="col-2">
                            <label> График:
                              <input type="file" accept="image/jpg,image/jpeg,image/png" @change="addThermographPicture(thermograph, $event)">
                            </label>
                          </td>
                          <td class="col-2"> Мин. темп. <input required v-model.lazy="thermograph.min" type="number" step="0.1" :max="thermograph.max"></td>
                          <td class="col-2"> Макс. темп. <input required v-model.lazy="thermograph.max" type="number" step="0.1" :min="thermograph.min"></td>
                        </tr>
                      </tbody>
                    </table>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="violations.length">
              <h4>
                Обнаружены нарушения температурного режима. Повлияли ли они на качество груза?
              </h4>
              <table style="width: 40%; display: inline-table">
                <tbody>
                  <tr
                      v-for="unit in this.violations"
                      :key="unit.number"
                      class="d-flex"
                  >
                    <td><b>ТЕ  {{unit.number}}</b></td>
                    <select required v-model.lazy="unit.temperature.violations_affect">
                      <option value="2">Нет</option>
                      <option value="3">Да</option>
                    </select>
                  </tr>
                </tbody>
              </table>
            </div>
            <br>
            <button
                type="submit"
                v-if="editable"
                class="btn btn-success">
              Сохранить данные температурных датчиков
            </button>
            <p v-if="editable" class="text-sm-center"><i> Внимание: вы не сможете изменить данные после сохранения! </i></p>
          </fieldset>
        </form>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      tableHeadersList: ['ТЕ', 'Рекомендованная темп.',	'Пульпа мин.',	'Пульпа макс.',	'Кол-во термографов',	'Состояние'],
      report: this.$store.state.report,
      thermographDataModel: this.$store.state.thermographDataModel,
      photoModel: this.$store.state.photoModel,
      editable: true
    }
  },
  emits: ["ThermalDataInsertedEvent"],
  computed: {
    violations() {
      let transportUnitsWithViolations = [];
      for (let unit of this.report.transport_units) {
        let temp = unit.temperature;
        if (Math.abs(temp.pulp.min - temp.recommended) > 2 ||
            Math.abs(temp.pulp.max - temp.recommended) > 2 ||
            temp.thermographs.some(thermograph => Math.abs(thermograph.min - temp.recommended) > 2 || Math.abs(thermograph.max - temp.recommended) > 2 )) {
          transportUnitsWithViolations.push(unit);
        } else {
          temp.violations_affect = '1';
        }
      }
      return transportUnitsWithViolations;
    },
  },
  methods: {
    continueReport() {
      this.$store.commit('setReport', this.report);
      this.$emit('ThermalDataInsertedEvent');
      this.editable = false;
      return false;
    },
    createThermographsList(transportUnit, numberOfThermographs) {
      transportUnit.temperature.thermographs = [];
      for (let i = 0; i < numberOfThermographs; i++) {
        transportUnit.temperature.thermographs.push(Object.assign({}, this.thermographDataModel))
      }
    },
    addThermographPicture(thermograph, event) {
      thermograph.graph = Object.assign({}, this.photoModel);
      let reader = new FileReader();
      reader.readAsDataURL(event.target.files[0]);
      reader.onload = event => {
          thermograph.graph.file = event.target.result;
      };
    },
  },
};
</script>

<style scoped>
</style>
