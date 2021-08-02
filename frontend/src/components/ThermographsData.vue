<template>
  <div class="container">
    <div class="row">
      <div>
        <br>
        <br>
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
              <td class="col-2">{{ unit.number }}</td>
              <td class="col-2"><input v-model.lazy="unit.temperature.recommended" type="number" step="0.1"></td>
              <td class="col-2"><input v-model.lazy="unit.temperature.min" type="number" step="0.1"></td>
              <td class="col-2"><input v-model.lazy="unit.temperature.max" type="number" step="0.1"></td>
              <td class="col-2">
                <select v-model.lazy="unit.thermographs">
                  <option value="0">0</option>
                  <option value="1">1</option>
                  <option value="2">2</option>
                </select>
              </td>
              <td class="col-2"><input type="checkbox" v-model="unit.selected"></td>
              <td class="col-2">
                <ul>
                  <li v-for="thermograph in unit.thermographs" :key="thermograph">
                    {{ thermograph }} термограф: <select v-model.lazy="unit.malfunctions[thermograph]">
                      <option value="yes">Работал</option>
                      <option value="did not work">Не работал</option>
                      <option value="did not work correctly">Работал некорректно</option>
                    </select>
                  </li>
                </ul>
              </td>
            </tr>
          </tbody>
        </table>
        <br>
        <button
            @click="continueReport"
            class="btn btn-success">
          Сохранить данные температурных датчиков
        </button>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      tableHeadersList: ['ТЕ', 'Рекомендованная темп.',	'Пульпа мин.',	'Пульпа макс.',	'Кол-во термографов',	'Состояние'],
      applicationsList: []
    };
  },
  props: ["report",],
  emits: ["ThermalDataInsertedEvent"],
  methods: {
    continueReport() {
      this.$emit('ThermalDataInsertedEvent')
    }
  },
};
</script>

<style scoped>
</style>
