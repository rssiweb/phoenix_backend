var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        heading: 'Students',
        token: Cookies.get('auth_token'),
        is_admin: (Cookies.get('is_admin')=='true'),
        students: [],
        categories: [],
        branches: [],

        categoryFilter: [],
        branchFilter: [],
        error: '',
        message: '',

        loading: '',
        studentToUpdate: {},
        isUpdate: false,

        loadedStudents: [],
        importing: '',
        importFile: undefined,
        imported: false,
        importSummary: '',

        initialized: false,
    },
    created: function(){
        console.log('created')
        this.load(['students', 'branches', 'categories'])
    },
    updated: function(){
        console.log('updated')
        if(!this.initialized && !this.loading){
            console.log('initialized')
            $(this.$el).find('table').tablesort()
            $(this.$el).find('.dropdown').dropdown()
            this.initialized = true
        }
    },
    methods: {
        importStudents: function(){
            this.importing = true;
            console.log('importing students from', this.importFile)
                //send the file to server and get list new students 
                //and list of updating students
                var vm = this;
                var url = '/api/admin/student/import'
                var postData = new FormData()
                postData.append('studentsListFile',this.importFile)
                vm.$http.post(url, postData, this.getHeaders())
                .then(response => {
                    console.log(response)
                    if(response.body.status=='success'){
                        response.body.updated.forEach((std, index)=>{
                            std.updated=true
                            vm.loadedStudents.push(std)
                        })
                        response.body.added.forEach((std, index)=>{
                            std.added=true
                            vm.loadedStudents.push(std)
                        });
                        vm.importSummary = response.body.added.length+' students Added, '+response.body.updated.length+' updated'
                        setTimeout(function(){
                            $('#importModal').modal('refresh')
                        }, 200)
                        if(response.body.added.length > 0 || response.body.updated.length > 0)
                            vm.loadStudents();
                    }else{
                        vm.importSummary = response.body.message
                    }
                    this.importing = false
                    this.imported = true
                },
                error => {
                    console.log(error)
                    this.importing = false
                    this.imported = true
                    this.importSummary = error.body.message || error.statusText
                });
            },
            loadStudents: function(){
                this.loading = 'Loading students...'
                var token = this.token;
                console.log('token', token)
                this.$http.get('/api/student')
                .then(data => {
                    console.log(data);
                    this.students = data.body.students

                    this.loading = ''
                },error => {
                    console.log(error)
                    this.error = error.body.message || error.statusText
                    this.loading = ''
                });
                if(this.students.length == 0){
                    if(data.body.message)
                        this.message = data.body.message
                    else
                        this.message = 'No students'
                }else{
                    this.message = ''
                    console.log('loaded')
                }
                console.log(this.message)
            },
            addOrUpdateStudent: function(){
                this.error = ''
                var url = ''
                if(this.studentToUpdate.id){
                    this.loading = 'Updating ' + this.studentToUpdate.name + '...'
                    url = '/api/admin/student/update'
                } else {
                    this.loading = 'Adding ' + this.studentToUpdate.name + '...'
                    url = '/api/admin/student/add'
                }

                var postData = this.getJsonFromForm('#addStudentForm')
                console.log(postData)
                var vm = this
                
                this.$http.post(url, postData)
                .then(response => {
                    console.log(response)
                    vm.loading = ''
                    if(response.body.status == 'fail'){
                        vm.error = this.constructErrorMessage(response.body.statusText,response.body.statusData)
                        return
                    }
                    // reset only if its success
                    vm.resetStudent()
                    var updatedStudent = response.body.student
                    console.log(updatedStudent)
                    if(!updatedStudent) return

                    var indexToreplace = -1
                    vm.students.forEach((tmpstd, index) => {
                        if(tmpstd.id == updatedStudent.id){
                            indexToreplace = index
                            console.log(index)
                        }
                    })
                    if(indexToreplace != -1){
                        vm.$set(vm.students, indexToreplace, updatedStudent)
                        console.log('setted')
                    }else{
                        vm.students.push(updatedStudent)
                    }
                    //get the new data from response and add him to the students list
                }, error => {
                    console.log(error)
                    vm.loading = ''
                })
            },
            updateStudent (id) {
                console.log(id)
                var stdToUpdate = null
                this.students.forEach(function(student, index){
                    if(student.id == id){
                        stdToUpdate = student
                        stdToUpdate.dob = moment(student.dob).format('YYYY-MM-DD')
                    }
                })
                if(!stdToUpdate) return
                this.isUpdate= true
                this.studentToUpdate = jQuery.extend({}, stdToUpdate)
                $(this.$el).find('#addStudentForm :input[name="category"]').dropdown('set selected', stdToUpdate.category)
            },
            resetStudent: function(){
                // clear the drop down and reset the studentToUpdate
                $(this.$el).find('#addStudentForm select').dropdown('clear')
                this.studentToUpdate = {}
                this.isUpdate = false
            },
            getJsonFromForm: function(formSelector){
                data = {}
                $(formSelector).find(':input').each(function(index, input){
                    data[input.name] = input.value
                    input.value = ''
                })
                return data
            },
            showImportModel(){
                $('#importModal').modal('show')
            },
            hideImportModel(){
                $('#importModal').modal('hide')
                this.clearImportState();
            },
            clearImportState(){
                this.loadedStudents = []
                this.importing = ''
                this.imported = false
                this.importSummary = ''
            },
        },
        computed:{
            buttonText: function(){
                if(this.isUpdate)
                    return "Update"       
                else
                    return "Add"
            },
            studentToUpdateFormattedDate:function(){
                if(this.studentToUpdate.dob)
                    return moment(this.studentToUpdate.dob).format('YYYY-MM-DD')
                else
                    return ''
            },
        },
    });