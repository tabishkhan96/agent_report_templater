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
              </tr>
            </thead>
            <tbody>
              <tr
                  v-for="unit in report.transport_units"
                  :key="unit.number"
                  class="d-flex"
              >
                <td class="col-2"><b>{{ unit.number }}</b></td>
                <td class="col-2">
                  Паллет: <input required v-model.lazy="unit.pallets" type="number"><br>
                  Коробок: <input required v-model.lazy="unit.boxes" type="number">
                </td>
                <td class="col-2">
                  <br>
                  <input required v-model.lazy="unit.damaged_pallets" type="number"><br><br>
                  <input required v-model.lazy="unit.damaged_boxes" type="number">
                </td>
                <td class="col-2">
                  <br>
                  <input placeholder=" -" disabled type="text" value=" - "><br><br>
                  <input required v-model.lazy="unit.cargo_damage" type="number">
                </td>
                <td class="col-2">
                  <br>
                  <input placeholder=" -" disabled type="text" value=" - "><br><br>
                  <input required v-model.lazy="unit.empty_boxes" type="number">
                </td>
                <td class="col-2">
                  <br>
                  <input placeholder=" -" disabled type="text" value=" - "><br><br>
                  <input required v-model.lazy="unit.not_full_boxes" type="number">
                </td>
              </tr>
            </tbody>
          </table>
            <br>
            <button
                v-if="editable"
                type="submit"
                class="btn btn-success">
              Сохранить паллеты/короба
            </button>
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
      tableHeadersList: ['ТЕ', 'Количество', 'Поврежденных паллет/тары',	'Повреждение груза',	'Пустые короба', 'С частичным отсутствием'],
      report: this.$store.state.report,
      editable: true
    }
  },
  emits: ["PalletDataInsertedEvent"],
  methods: {
    continueReport() {
      this.$store.commit('setReport', this.report);
      this.$emit('PalletDataInsertedEvent');
      this.editable = false;
      return false;
    },
  },
};
</script>

<style scoped>
</style>
