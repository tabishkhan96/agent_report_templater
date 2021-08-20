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
                v-for="application in applicationsList"
                :key="application.id"
                class="d-flex"
                @click="application.selected=!application.selected"
            >
              <td class="col-2"><input type="checkbox" v-model="application.selected"></td>
              <td class="col-2" style="cursor: pointer; text-decoration: underline;">
                {{ application.transport_unit }}
              </td>
              <td class="col-2">{{ application.order }}</td>
              <td class="col-2">{{ application.supplier }}</td>
              <td class="col-2">{{ application.BL }}</td>
              <td class="col-2">{{ application.vessel }}</td>
              <td class="col-2">{{ application.cargo }}</td>
              <td class="col-2">{{ application.card }}</td>
              <td class="col-2">{{ application.cultivar }}</td>
              <td class="col-2">{{ application.units }}</td>
              <td class="col-2">{{ application.invoice }}</td>
              <td class="col-2">{{ application.date.toLocaleDateString() }}</td>
              <td class="col-2">{{ application.calibre }}</td>
              <td class="col-2">{{ application.terminal }}</td>
              <td class="col-2">{{ application.expeditor }}</td>
            </tr>
          </tbody>
        </table>
        <br>
        <button
            v-if="hasSelected"
            @click="continueReport"
            class="btn btn-success">
          Составить отчет для выбранных ТЕ
        </button>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      tableHeadersList: ['', 'ТЕ', 'Заказ',	'Поставщики',	'Коносаменты',	'Суда',	'Грузы',	'Карточки',	'Сорта',	'Ед.',	'Инвойсы',	'Примерная дата',	'Калибры',	'Терминалы',	'Экспедиторы'],
      applicationsList: this.convertFieldsFromRussianToEnglish(this.applicationsJsonList)
    };
  },
  props: ["applicationsJsonList"],
  emits: ["ApplicationsSelectedEvent"],
  computed: {
    hasSelected() {
      return this.applicationsList.some(function (element) {return element.selected})
    }
  },
  methods: {
    convertFieldsFromRussianToEnglish (jsonList) {
      return jsonList.map(o => ({
          id: jsonList.indexOf(o),
          selected: false,
          order: o["заказ"] || o["Заказ"],
          supplier: o["поставщик"] || o["Поставщик"] || "",
          BL: o["коносамент"].toString() || "",
          transport_unit: o["контейнер"] || "",
          vessel: o["судно"] || "",
          cargo: o["груз"] || "",
          card: o["карточка"] || "",
          cultivar: o["сорт"] || "",
          units: o["ед.-измерения"] || "",
          invoice: o["инвойс"].toString() || "",
          date: o["примерная-дата"],
          calibre: o["калибр"] || "",
          terminal: o["Терминал"] || "",
          expeditor: o["экспедитор"] || "",
          organization: o["Организация"] || "",
          remark: o["примечание"] || "",
        }));
    },
    saveReport() {
      this.$store.commit('setReport', this.report);
      this.$emit('ApplicationsSelectedEvent');
    },
    continueReport() {
      let report = null;
      this.applicationsList.forEach(function (application) {
        if (application.selected) {
          if (report) {
            if (report.order !== application.order) {
              return;
            }
            if (!report.vessel.includes(application.vessel)) {
              report.vessel = [report.vessel, application.vessel].flat();
            }
            let unitIndex;
            // eslint-disable-next-line no-unused-vars
            if (report.transport_units.some(function (element, index, array) {
              unitIndex = index;
              return element.number === application.transport_unit;
            })) {
              report.transport_units[unitIndex].cargo.push(application.cargo);
              report.transport_units[unitIndex].card.push(application.card);
              report.transport_units[unitIndex].cultivar.push(application.cultivar);
              report.transport_units[unitIndex].units.push(application.units);
            } else {
              report.transport_units.push({
                number: application.transport_unit,
                supplier: application.supplier,
                cargo: [application.cargo],
                card: [application.card],
                cultivar: [application.cultivar],
                units: [application.units],
                invoice: application.invoice,
                date: application.date,
                calibre: [application.calibre],
              });
            }
          } else {
            report = {
              order: application.order,
              report_number: application.report_number,
              place_of_inspection: application.place_of_inspection,
              inspection_date: application.inspection_date,
              vessel: application.vessel,
              transport_units: [{
                number: application.transport_unit,
                supplier: application.supplier,
                cargo: [application.cargo],
                card: application.card,
                cultivar: application.cultivar,
                units: application.units,
                invoice: application.invoice,
                date: application.date,
                calibre: application.calibre,
              }]
            };
          }
        }
      });
      this.$emit('applicationsSelectedEvent', report);
    },
  },
};
</script>

<style scoped>
</style>
