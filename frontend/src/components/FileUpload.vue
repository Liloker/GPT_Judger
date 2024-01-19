<template>
    <div class="container">
        <!-- <pre>{{ codeAnalysis2 }}</pre> -->
        <div class="upload-area">
            <!-- <el-upload 
            action="https://run.mocky.io/v3/19e17875-bdd2-4ae4-a66b-8c778e9b3fa9" 
            :on-success="handleSuccess"
            :limit="1" multiple drag> -->
            <el-upload 
            action="http://127.0.0.1:5431/upload" 
            :on-progress="handleProgress"
            :on-success="handleSuccess"
            :limit="1" multiple drag
            name="file">
            <!--  -->
            <!-- 指定上传文件对象key为file -->
            <i class="el-icon-upload"></i>
            <div class="el-upload__text"><em>选择文件</em></div>
            <!-- <el-button slot="trigger" size="small" type="primary">选择文件</el-button> -->
              <!-- <el-button type="primary" @click="handleProgress2">开始分析</el-button> -->
            <!-- <div slot="tip" class="el-upload__tip">支持py, java, c, cpp, js, html, css</div> -->
            </el-upload>
             <!-- <div :v-loading="loading" class="result-area" v-if="codeScore !== null"> -->
        </div>
        <div  class="result-area">
            <!-- :v-loading="loading" <h2>代码评分：{{ codeScore }}</h2> -->
            <h2>代码评分：</h2>
            <pre>{{ codeAnalysis }}</pre>
            <!-- <pre>{{ HowToUse }}</pre> -->
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { ElUpload, ElLoading } from "element-plus";


// const codeScore = ref(null);
const HowToUse = ref("");
HowToUse.value = "\n示例：\n这段代码的作用是XXXXXXXXXX。\n代码质量各项满分10分，分数如下：\n\n1. 代码注释：8分，注释清晰明了，能很好地理解代码的功能，但有个别地方的注释不全，缺少了对输入输出参数的注释。\n2. 命名规范：8分，大部分变量和函数的命名都很规范，能准确反应其作用，但'iv', 'e', 'd'等变量命名过于简单，不够清晰。\n3. 代码格式：8分，大部分代码格式整齐，但部分代码存在没有适当空格的情况，影响了代码的可读性，例如在运算符两侧应有空格。\n4. 代码冗余：8分，在代码cond字符串进行补足位数时有一定冗余，并且密钥生成的方式和返回方式有待改进，可以将这部分单独作为密钥处理函数，提高代码可复用性。\n5. 代码安全：7分，采取了基于AES的加密算法，安全性较高，但在主函数中直接接收并使用输入的密钥可能存在风险，应该对输入的密钥进行有效性检查。\n6. 运行性能：7分，代码逻辑清晰，但在补足字符串长度和进行加密解密操作时存在一定的性能浪费。\n\n这段代码的总体评价是：代码质量较高，注释清晰，结构定义合理，能实现预期功能，但部分代码存在冗余，且部分地方的安全性和效率有待改进。\n\n这段代码的改进建议是：\n1. 对输入的密钥进行有效性检查，避免安全风险。\n2. 优化补足字符串长度和加密解密操作的代码，提高代码执行效率。\n3. 增强代码的健壮性，对输入输出进行异常处理。\n4. 增加更详细的注释，提高代码可读性。"
const codeAnalysis = ref("");
codeAnalysis.value = HowToUse.value;

const loading = ref(null);

const handleProgress = () => {
        loading.value = ElLoading.service({
        fullscreen: false,
        // target: ,
        lock: true,
        text: '正在分析中，请耐心等待',
        spinner: 'el-icon-loading',
        // background: 'rgba(0, 0, 0, 0.1)'
    });
}

const handleSuccess = (response) => {
     // 判断响应的状态码是否为0，表示成功
    if (response.code === 0) {
        // codeScore.value = response.data.number;
        
        // codeAnalysis.value = response.data.text;
        codeAnalysis.value = JSON.parse(response.data.text);
        // str = str.replace(/\n/g, "<br>") // 将\n替换为<br>
        loading.value.close();
    } else {
        // 否则，提示响应的错误信息
        alert(response.msg);
    }
};
</script>

<style scoped>
.container {
    width: 1200px;
    margin: 0 auto;
}

.upload-area {
    border: 2px dashed #ccc;
    padding: 20px;
    text-align: center;
    /* max-width: 800px; */
}

.result-area {
    margin-top: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    text-align: left;
    /* max-width: 800px; */
    /* overflow-wrap: break-word;  */
    /* 设置超出宽度时在单词边界处换行 */
}

.loading-area {
    margin-top: 20px;
    padding: 20px;
    border: 1px solid #ccc;
    text-align: center;
}

/* pre {
  max-width: 800px; 
  overflow-wrap: break-word; 
} */
</style>




