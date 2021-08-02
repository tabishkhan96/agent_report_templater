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
        <button v-if="inspectionDate" @click="$refs.file.click()" class="btn btn-success">Выберите файл заявки...</button>
        <br>
        <br>
        <ImportApplicationsTable
            v-if="importApplication && showTable"
            :applications-json-list="applicationsList"
            :report-number="reportNumber"
            :place-of-inspection="placeOfInspection"
            :inspection-date="inspectionDate"
            @applicationsSelectedEvent="beginMakingReport"
        ></ImportApplicationsTable>
        <ThermographsData
            v-if="applicationsSelected"
            :report="report"
            @ThermalDataInsertedEvent="toPalletsData"
        ></ThermographsData>
        <button v-if="textFinished" @click="createReportForOrder" class="btn btn-success">Создать текстовую часть отчета</button>
        <Gallery v-if="attachPhotos" :doc-guid="docGuid"></Gallery>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import XLSX from 'xlsx';
import Gallery from './Gallery.vue';
import ImportApplicationsTable from "./ImportApplicationsTable";
import ThermographsData from "./ThermographsData";

export default {
  data() {
    return {
      applicationsList: [],
      placeOfInspection: 'РЦ Альфа Центавра / RC Alpha Centauri',
      reportNumber: 'IL-NS-0',
      inspectionDateRow: '',
      twoDaysInspection: false,
      importApplication: false,
      showTable: true,
      applicationsSelected: false,
      attachPhotos: false,
      report: {},
      docGuid: '',
      message: ''
    };
  },
  components: {
    Gallery,
    ImportApplicationsTable,
    ThermographsData,
  },
  computed: {
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
  },
  methods: {
    addApplicationFile(event) {
      let file = event.target.files[0];
      this.getApplicationsFromFile(file, this.afterFileLoad);
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
    afterFileLoad(jsonList) {
      this.applicationsList = jsonList;
      this.resolveApplicationType(this.applicationsList);
    },
    resolveApplicationType(jsonList) {
      if (jsonList[0]["контейнер"] || jsonList[0]["Контейнер"]) {
        this.importApplication = true;
      }
    },
    resetGlobalVariables() {
      this.attachPhotos = false;
      this.photosSet = false;
      this.picturesList = [];
      this.docReceived = false;
      this.importApplication = false;
      this.showTable = true;
      this.applicationsSelected = false;
    },
    beginMakingReport(reportObj) {
      this.showTable = false;
      this.report = reportObj;
    },
    async createReportForOrder(orderNumber) {
      this.applicationsList = this.applicationsList.filter(application => application.order === orderNumber);
      let order = this.orders[orderNumber];
      try {
        const res = await axios.put('http://0.0.0.0:8080/report/', order);
        this.attachPhotos = true;
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
