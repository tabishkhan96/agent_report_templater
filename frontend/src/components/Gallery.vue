<template>
  <div class="container">
    <div class="row">
      <div>
        <div v-if="message" class="alert">{{ message }}<span class="closebtn" @click="message=''">&times;</span></div>
        <br>
        <input type="file" multiple ref="pictures" accept="image/jpg,image/jpeg,image/png" style="display: none" @change="getPicturesFromField">
        <button @click="$refs.pictures.click()" class="btn btn-success" style="margin: 15px">
          Выберите фотографии...
        </button>
        <br>
        <table style="margin: auto">
          <tr v-for="chunk in picturesListChunked" :key="chunk" class="d-flex">
            <td @drop='onDrop($event, chunk[0])'
                @dragover.prevent
                @dragenter.prevent
                class="picture-cell"
            >
              <img :src="chunk[0].obj" alt="picture" draggable @dragstart='startDrag($event, chunk[0])'/><br>
              <span class="deletebtn" @click="picturesList.splice(chunk[0].id, 1)" style="color: black">&times;</span>
            </td>
            <td v-if="chunk[1]"
                @drop='onDrop($event, chunk[1])'
                @dragover.prevent
                @dragenter.prevent
                class="picture-cell"
            >
              <img :src="chunk[1].obj" alt="picture" draggable @dragstart='startDrag($event, chunk[1])'/><br>
              <span class="deletebtn" @click="picturesList.splice(chunk[1].id, 1)">&times;</span>
            </td>
          </tr>
        </table>
        <button v-if="photosSet" @click="picturesList.reverse();recountPictureList()" class="btn" style="margin: 15px">
          Обратный порядок
        </button>
        <button v-if="photosSet" @click="deleteAll" class="btn" style="margin: 15px">
          Удалить все
        </button>
        <br>
        <button v-if="photosSet && !docReceived" @click="uploadPhotos" class="btn btn-success">
          Отправить
        </button>
        <br>
        <a ref="getAgain"></a>
        <button v-if="docReceived" @click="$refs.getAgain.click()" class="btn btn-success" style="margin: 15px">
          Скачать повторно
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      photosSet: false,
      picturesList: [],
      pictureTypes: ['image/jpg','image/jpeg','image/png'],
      docReceived: false,
      message: ''
    };
  },
  props: ["docGuid"],
  computed: {
    picturesListChunked() {
      let result = [];
      for (let i = 0; i < this.picturesList.length; i += 2) {
        result.push(this.picturesList.slice(i, i + 2))
      }
      return result;
    }
  },
  methods: {
    getPicturesFromField(event) {
      let files = event.target.files;
      for (let i=0; i<files.length;i++) {
        if (!this.pictureTypes.includes(files[i].type)) {
          this.message = `Неверный формат ${i+1} фотографии!`;
          return
        }
      }
      this.message = '';
      this.photosSet = true;
      this.setIDsForPictures(files);
    },
    async setIDsForPictures(files) {
      files = Array.from(files).sort((f1, f2) => f1.lastModified - f2.lastModified);
      for (let i = 0; i < files.length; i++) {
        let reader = new FileReader();
        reader.readAsDataURL(files[i]);
        reader.onload = event => {
            this.picturesList.push({id: i, obj: event.target.result, file: files[i]});
        };
      }
    },
    recountPictureList() {
      for (let i = 0; i < this.picturesList.length; i++) {
        this.picturesList[i].id = i;
      }
    },
    deleteAll() {
      if (confirm("Удалить все фотографии?")) {
        this.picturesList = [];
        this.photosSet = false;
      }
    },
    startDrag: (event, image) => {
      event.dataTransfer.dropEffect = 'move';
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('imageID', image.id);
    },
    onDrop (event, target) {
      const targetID = target.id;
      const imageID = Number(event.dataTransfer.getData('imageID'));
      const image = this.picturesList.find(img => img.id === imageID)
      image.id = targetID;
      if (targetID > imageID) {
        this.picturesList.splice(targetID+1, 0, image);
        this.picturesList.splice(imageID, 1);
      } else if (targetID < imageID) {
        this.picturesList.splice(targetID, 0, image);
        this.picturesList.splice(imageID+1, 1);
      }
      this.recountPictureList();
    },
    async uploadPhotos () {
      let data = new FormData();
      for (let i = 0; i < this.picturesList.length; i++ ) {
         data.append('pictures', this.picturesList[i].file);
      }
      let config = {header : {'Content-Type' : 'multipart/form-data'}, responseType: 'blob'};
      try {
        let res = await axios.patch(`http://0.0.0.0:8080/report/${this.docGuid}`, data, config);
        let blob = new Blob([res.data], {type: res.headers["content-type"]});
        let fileName = res.headers["content-disposition"].split("filename*=utf-8''")[1];
        let link = this.$refs['getAgain'];
        link.href = window.URL.createObjectURL(blob);
        link.download = fileName;
        link.click();
        this.photosSet = false;
        this.docReceived = true;
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
  .deletebtn {
    margin-left: 15px;
    color: black;
    font-size: 22px;
    line-height: 20px;
    cursor: pointer;
    transition: 0.3s;
  }

  .picture-cell {
    padding: 5px;
    box-shadow: 0 0 9px 0 rgba(0,0,0,0.1);
    border-radius: 3px;
  }

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
