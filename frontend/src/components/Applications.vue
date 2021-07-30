<template>
  <div class="container">
    <div class="row">
      <div>
        <h1> Сюрвейерские отчеты </h1>
        <hr>
        <br>
        <div v-if="message" class="alert">{{ message }}<span class="closebtn" @click="message=''">&times;</span></div>
        <br>
        <label> Место проведения инспекции <input v-model.lazy="placeOfInspection" size="50"/></label><br>
        <label> Номер отчета <input v-model.lazy="reportNumber"/></label><br>
        <label> Дата инспекции
          <input type="date" v-model.lazy="inspectionDateRow"/> &nbsp;
          <label v-if="inspectionDateRow"> добавить следующий день: <input type="checkbox" v-model="twoDaysInspection"/> </label>
        </label>
        <br>
        <input type="file"
               ref="file"
               accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
               style="display: none"
               @change="addApplicationFile"
        >
        <button @click="$refs.file.click()" class="btn btn-success">Выберите файл заявки...</button>
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
            <tr v-for="order in orders" :key="order.order" class="d-flex">
              <td class="col-2" @click="createReportForOrder(order.order)" style="cursor: pointer; text-decoration: underline;">
                {{ order.order }}
              </td>
              <td class="col-2">{{ order.supplier.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.BL.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.containers.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.vessel.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.cargo.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.card.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.cultivar.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.units.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.invoice.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ dateToString(order.date).replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.calibre.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.terminal.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.expeditor.toString().replaceAll(',', '\n') }}</td>
              <td class="col-2">{{ order.remark.toString().replaceAll(',', '\n') }}</td>
            </tr>
          </tbody>
        </table>
        <br>
        <Gallery v-if="orderSelected" :doc-guid="docGuid"></Gallery>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import XLSX from 'xlsx';
import Gallery from './Gallery.vue'

export default {
  data() {
    return {
      tableHeadersList: ['Заказ',	'Поставщики',	'Коносаменты',	'Контейнеры',	'Судна',	'Грузы',	'Карточки',	'Сорта',	'Ед.',	'Инвойсы',	'Примерная дата',	'Калибры',	'Терминалы',	'Экспедиторы',	'Примечания'],
      applicationsList: [],
      placeOfInspection: 'РЦ Альфа Центавра / RC Alpha Centauri',
      reportNumber: 'IL-NS-0',
      inspectionDateRow: '',
      twoDaysInspection: false,
      orderSelected: false,
      docGuid: '',
      message: ''
    };
  },
  components: {
    Gallery
  },
  computed: {
    orders() {
      let orders = {};
      this.applicationsList.forEach(function (application) {
        if (application.order in orders) {
          if (!orders[application.order].supplier.includes(application.supplier)) {
            orders[application.order].supplier = [orders[application.order].supplier, application.supplier].flat();
          }
          if (!orders[application.order].BL.includes(application.BL)) {
            orders[application.order].BL = [orders[application.order].BL, application.BL].flat();
          }
          if (!orders[application.order].containers.includes(application.containers[0])) {
            orders[application.order].containers = [orders[application.order].containers, application.containers].flat();
          }
          if (!orders[application.order].cargo.includes(application.cargo)) {
            orders[application.order].cargo = [orders[application.order].cargo, application.cargo].flat();
          }
          if (!orders[application.order].card.includes(application.card)) {
            orders[application.order].card = [orders[application.order].card, application.card].flat();
          }
          if (!orders[application.order].cultivar.includes(application.cultivar)) {
            orders[application.order].cultivar = [orders[application.order].cultivar, application.cultivar].flat();
          }
          if (!orders[application.order].units.includes(application.units)) {
            orders[application.order].units = [orders[application.order].units, application.units].flat();
          }
          if (!orders[application.order].invoice.includes(application.invoice)) {
            orders[application.order].invoice = [orders[application.order].invoice, application.invoice].flat();
          }
          if ((Array.isArray(orders[application.order].date) && !orders[application.order].date.includes(application.date)) ||
              (!Array.isArray(orders[application.order].date) && orders[application.order].date !== application.date)) {
            orders[application.order].date = [orders[application.order].date, application.date].flat();
          }
          if (!orders[application.order].calibre.includes(application.calibre)) {
            orders[application.order].calibre = [orders[application.order].calibre, application.calibre].flat();
          }
          if (!orders[application.order].terminal.includes(application.terminal)) {
            orders[application.order].terminal = [orders[application.order].terminal, application.terminal].flat();
          }
          if (!orders[application.order].expeditor.includes(application.expeditor)) {
            orders[application.order].expeditor = [orders[application.order].expeditor, application.expeditor].flat();
          }
          if (!orders[application.order].organization.includes(application.organization)) {
            orders[application.order].organization = [orders[application.order].organization, application.organization].flat();
          }
          if (!orders[application.order].remark.includes(application.remark)) {
            orders[application.order].remark = [orders[application.order].remark, application.remark].flat();
          }
        } else {
          orders[application.order] = application;
        }
      });
      return orders;
    },
    inspectionDate () {
      let date = '';
      if (this.inspectionDateRow) {
        date = new Date(this.inspectionDateRow);
        date = date.toLocaleDateString();
      }
      if (this.twoDaysInspection) {
        let secondDay = new Date(this.inspectionDateRow);
        secondDay.setDate(secondDay.getDate() + 1);
        date += ` - ${secondDay.toLocaleDateString()}`;
      }
      return date;
    },
    picturesListChunked() {
      let result = [];
      for (let i = 0; i < this.picturesList.length; i += 2) {
        result.push(this.picturesList.slice(i, i + 2))
      }
      return result;
    }
  },
  methods: {
    addApplicationFile(event) {
      let file = event.target.files[0];
      this.getApplicationsFromFile(file, this.convertFieldsFromRussianToEnglish);
    },
    async getApplicationsFromFile(file, callback) {
      this.resetGlobalVariables();
      let reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.onload = async function () {
        let data = new Uint8Array(reader.result);
        let workbook = XLSX.read(data, {type: 'array', cellDates: true});
        callback(XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]]));
      };
    },
    resetGlobalVariables() {
      this.orderSelected = false;
      this.photosSet = false;
      this.picturesList = [];
      this.docReceived = false;
    },
    convertFieldsFromRussianToEnglish (jsonList) {
      this.applicationsList = jsonList.map(o => ({
          order: o["заказ"],
          report_number: this.reportNumber,
          place_of_inspection: this.placeOfInspection,
          inspection_date: this.inspectionDate,
          supplier: o["поставщик"] || "",
          BL: o["коносамент"].toString() || "",
          containers: [o["контейнер"]] || [],
          vessel: o["судно"] || "",
          cargo: o["груз"] || "",
          card: o["карточка"] || "",
          cultivar: o["сорт"] || "",
          units: o["ед.-измерения"] || "",
          invoice: o["инвойс"].toString() || "",
          date: o["примерная-дата"].getTime(),
          calibre: o["калибр"].toString() || "",
          terminal: o["Терминал"].toString() || "",
          expeditor: o["экспедитор"] || "",
          organization: o["__EMPTY"] || "",
          remark: o["примечание"] || "",
        }));
    },
    dateToString(dateOrDateList) {
       if (!dateOrDateList) return "Date not set!";
       if (Array.isArray(dateOrDateList)) {
         return dateOrDateList.map(date => new Date(date).toLocaleDateString()).toString();
       } else {
         return new Date(dateOrDateList).toLocaleDateString();
       }
    },
    async createReportForOrder(orderNumber) {
      this.applicationsList = this.applicationsList.filter(application => application.order === orderNumber);
      let order = this.orders[orderNumber];
      try {
        const res = await axios.put('http://0.0.0.0:8080/report/', order);
        this.orderSelected = true;
        this.message = '';
        this.docGuid = res.data;
      } catch (error) {
        this.message = "Не удалось создать документ!";
        // eslint-disable-next-line
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
  .alert {
    padding: 20px;
    background-color: #f44336; /* Red */
    color: white;
    font-weight: bold;
    margin-bottom: 15px;
  }

  /* The close button */
  .closebtn {
    margin-left: 15px;
    color: white;
    float: right;
    font-size: 22px;
    line-height: 20px;
    cursor: pointer;
    transition: 0.3s;
  }

  /* When moving the mouse over the close button */
  .closebtn:hover {
    color: black;
  }
</style>
