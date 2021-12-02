<template>
  <div>
    <h1> Сюрвейерские отчеты </h1>
    <hr>
    <br>
    <div v-if="message" class="alert">{{ message }}<span class="closebtn" @click="message=''">&times;</span></div>
    <br>
    <div class="container">
      <div class="row">
        <table class="table table-hover">
          <tbody>
            <tr class="d-flex">
              <td style="text-align: left">
                <label> Номер отчета <input v-model.lazy="reportNumber"/></label>
              </td>
              <td style="text-align: right">
                <label> Место проведения инспекции <input v-model.lazy="placeOfInspection" size="50"/></label>
              </td>
            </tr>
            <tr class="d-flex">
              <td style="text-align: left">
                <label> Дата инспекции
                  <input type="date" v-model.lazy="inspectionDateRow"/> &nbsp;
                  <label v-if="inspectionDateRow"> добавить следующий день: <input type="checkbox" v-model="twoDaysInspection"/> </label>
                </label>
              </td>
              <td style="text-align: right">
                <label> Имя и фамилия инспектора: рус.:<input v-model.lazy="surveyor"/><br> англ.:<input style="margin-top: 5px" v-model.lazy="surveyorEng"/></label>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <input type="file"
           ref="applicationFile"
           accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
           style="display: none"
           @change="addApplicationFile"
    >
    <button v-if="inspectionDate" @click="$refs.applicationFile.click" class="btn btn-success">Выберите файл заявки...</button>
    <br>
    <br>
    <SelfImportApplicationsTable
        v-if="selfImportApplication && showTable"
        :applications-json-list="applicationsList"
        @ApplicationsSelectedEvent="toThermalData"
    ></SelfImportApplicationsTable>
    <ThermographsData
        v-if="applicationsSelected"
        @ThermalDataInsertedEvent="toPalletsData"
    ></ThermographsData>
    <PalletsData
      v-if="thermalDataSet"
      @PalletDataInsertedEvent="textFinished=true;"
    ></PalletsData>
    <br>
    <button v-if="textFinished" @click="createReport" class="btn btn-success">Создать текстовую часть отчета</button>
    <input type="file"
           ref="editedReportFile"
           accept="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
           style="display: none"
           @change="replaceReport($event)"
    >
    <button v-if="attachPhotos" @click="$refs.editedReportFile.click" class="btn btn-primary">
      Отправить измененный отчет
    </button>
    <br>
    <div v-if="attachPhotos">
      <div v-for="transport_unit in report.transport_units" :key="transport_unit.number">
        <h3> {{ transport_unit.number }} </h3>
        <Gallery :transport-unit-number="transport_unit.number"></Gallery>
      </div>
    </div>
    <button v-if="attachPhotos" @click="sendReportWithPhotos" class="btn btn-success" style="margin: 10px">
      Отправить фотографии
    </button>
    <br>
    <a href="#" ref="downloadDocument"></a>
    <button v-if="docFileName" @click="$refs.downloadDocument.click" class="btn btn-info" style="margin: 10px">
      Скачать повторно
    </button>
    <br>
    <button v-if="reportFinished" @click="resetGlobalVariables(true)" class="btn btn-success" style="margin: 10px">
      Вернуться в начало
    </button>
  </div>
</template>

<script>
import axios from 'axios';
import XLSX from 'xlsx';
import Gallery from './Gallery.vue';
import SelfImportApplicationsTable from "./SelfImportApplicationsTable";
import ThermographsData from "./ThermographsData";
import PalletsData from "./PalletsData";

export default {
  data() {
    return {
      applicationsList: [],
      placeOfInspection: 'РЦ Альфа Центавра / RC Alpha Centauri',
      reportNumber: 'IL-NS-0',
      inspectionDateRow: '',
      twoDaysInspection: false,
      surveyor: '',
      surveyorEng: '',
      selfImportApplication: false,
      showTable: true,
      applicationsSelected: false,
      thermalDataSet: false,
      textFinished: false,
      attachPhotos: false,
      docFileName: '',
      reportFinished: false,
      message: ''
    };
  },
  components: {
    Gallery,
    SelfImportApplicationsTable,
    ThermographsData,
    PalletsData,
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
    report () {
      let report = this.$store.state.report;
      report.place_of_inspection = this.placeOfInspection;
      report.number = this.reportNumber;
      report.inspection_date = this.inspectionDate;
      report.surveyor = this.surveyor + ' / ' + this.surveyorEng;
      return report
    }
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
        this.selfImportApplication = true;
      }
      this.saveReport();
    },
    saveReport() {
      this.$store.commit('setReport', this.report)
    },
    dropReport() {
      this.$store.commit('dropReport')
    },
    resetGlobalVariables(all=false) {
      if (all) {
        this.inspectionDateRow = '';
        this.twoDaysInspection = false;
      }
      this.attachPhotos = false;
      this.selfImportApplication = false;
      this.showTable = true;
      this.applicationsSelected = false;
      this.textFinished = false;
      this.thermalDataSet = false;
      this.docFileName = '';
      this.reportFinished = false;
      this.dropReport();
    },
    toThermalData() {
      this.applicationsSelected = true;
      this.scrollToBottom()
    },
    toPalletsData() {
      this.thermalDataSet = true;
      this.scrollToBottom()
    },
    scrollToBottom() {
      setTimeout(window.scrollTo, 100, 0, document.body.scrollHeight);
    },
    async createReport() {
      let config = {header : {'Content-Type' : 'application/json'}, responseType: 'blob'};
      try {
        const res = await axios.put('http://0.0.0.0:8080/report/', this.report, config);
        let blob = new Blob([res.data], {type: res.headers["content-type"]});
        let fileName = res.headers["content-disposition"].split("filename*=utf-8''")[1];
        let link = this.$refs.downloadDocument;
        link.href = window.URL.createObjectURL(blob);
        link.download = decodeURIComponent(fileName);
        link.click();
        this.docFileName = fileName;
        this.attachPhotos = true;
        this.message = '';
        this.textFinished = false;
        this.scrollToBottom();
      } catch (error) {
        this.message = "Не удалось создать документ!";
        // eslint-disable-next-line
        console.error(error);
      }
    },
    async replaceReport(event) {
      let formData = new FormData();
      formData.append('report_file', event.target.files[0]);
      let encodedFileName = encodeURIComponent(this.docFileName);
      let config = {headers : {'Content-Type': 'multipart/form-data'}};
      try {
        await axios.post(`http://0.0.0.0:8080/report/${encodedFileName}`, formData, config);
      } catch (error) {
        this.message = "Не удалось заменить документ!";
        // eslint-disable-next-line
        console.error(error);
      }
    },
    async sendReportWithPhotos() {
      console.log(this.report);
      let config = {header : {'Content-Type' : 'application/json'}, responseType: 'blob'};
      try {
        const res = await axios.patch('http://0.0.0.0:8080/report/', this.report, config);
        let blob = new Blob([res.data], {type: res.headers["content-type"]});
        let link = this.$refs.downloadDocument;
        link.href = window.URL.createObjectURL(blob);
        link.click();
        this.attachPhotos = false;
        this.reportFinished = true;
      } catch (error) {
        this.message = "Не удалось добавить фотографии!";
        // eslint-disable-next-line
        console.error(error);
      }
    }
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
