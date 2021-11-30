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
            <td @drop="onDrop($event, chunk[0])"
                @dragover.prevent
                @dragenter.prevent
                class="picture-cell"
            >
              <img
                  :src="chunk[0].file"
                  alt="Picture was not loaded:("
                  class="picture"
                  :style="'transform: rotate(' + chunk[0].rotation + 'deg);'"
                  draggable
                  @dragstart="startDrag($event, chunk[0])"/>
              <div class="caption">
                <span class="manipulation-btn" @click="rotatePictureClockwise(chunk[0].id)">&#8635;</span>
                <span class="manipulation-btn" @click="rotatePictureCounterClockwise(chunk[0].id)">&#8634;</span>
                <span class="manipulation-btn" @click="picturesList.splice(chunk[0].id, 1)">&times;</span>
              </div>
            </td>
            <td v-if="chunk[1]"
                @drop='onDrop($event, chunk[1])'
                @dragover.prevent
                @dragenter.prevent
                class="picture-cell"
            >
              <img
                  :src="chunk[1].file"
                  alt="Picture was not loaded:("
                  class="picture"
                  :style="'transform: rotate(' + chunk[1].rotation + 'deg);'"
                  draggable
                  @dragstart="startDrag($event, chunk[1])"/>
              <div class="caption">
                <span class="manipulation-btn" @click="rotatePictureClockwise(chunk[1].id)">&#8635;</span>
                <span class="manipulation-btn" @click="rotatePictureCounterClockwise(chunk[1].id)">&#8634;</span>
                <span class="manipulation-btn" @click="picturesList.splice(chunk[1].id, 1)">&times;</span>
              </div>
            </td>
          </tr>
        </table>
        <button v-if="photosSet" @click="picturesList.reverse();recountPictureList()" class="btn btn-secondary" style="margin: 15px">
          Обратный порядок
        </button>
        <button v-if="photosSet" @click="savePhotos" class="btn btn-success" style="margin: 15px">
          Сохранить
        </button>
        <button v-if="photosSet" @click="deleteAll" class="btn btn-warning" style="margin: 15px">
          Удалить все
        </button>
        <br>
      </div>
    </div>
  </div>
</template>

<script>

export default {
  data() {
    return {
      photosSet: false,
      picturesList: [],
      pictureTypes: ['image/jpg','image/jpeg','image/png'],
      report: this.$store.state.report,
      message: ''
    };
  },
  props: ["transportUnitNumber"],
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
            this.picturesList.push({id: i, file: event.target.result, rotation: 0});
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
        this.savePhotos();
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
    savePhotos() {
      let transport_unit = this.report.transport_units.filter(unit => unit.number === this.transportUnitNumber)[0];
      transport_unit.photos = [...this.picturesList];
      this.$store.commit('setReport', this.report);
    },
    rotatePictureClockwise(id) {
      this.picturesList[id].rotation += 90;
      if (this.picturesList[id].rotation >= 360) {
        this.picturesList[id].rotation -= 360;
      }
    },
    rotatePictureCounterClockwise(id) {
      this.picturesList[id].rotation -= 90;
      if (this.picturesList[id].rotation < 0) {
        this.picturesList[id].rotation += 360;
      }
    }
  },
};
</script>

<style scoped>
  .manipulation-btn {
    margin: 0 5px;
    vertical-align: middle;
    color: black;
    font-size: 22px;
    line-height: 20px;
    cursor: pointer;
    transition: 0.3s;
  }

  .picture {
    width: 80%;
  }

  .picture-cell {
    overflow: hidden;
    width: 50%;
    padding: 10px;
    box-shadow: 0 0 10px 0 rgba(0,0,0,0.1);
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

  .caption {
    display: block;
    width: 120px;
    left: 40%;
    right: 40%;
    padding: 10px;
    position: relative;
    background-color: white;
    border-radius: 5px;
    opacity: .7;
    bottom: 50px;
    z-index: 3;
    text-align: center;
  }
</style>
