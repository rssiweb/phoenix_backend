var app = new Vue({
    mixins: [utils],
    el: '#app',
    data: {
        heading: 'Students',
        students: [],
        categories: [],
        branches: [],

        categoryFilter: [],
        branchFilter: [],
        statusFilter: 'all',
        searchTxt: '',

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

        studentModalError: '',
        initialized: false,
        studentForm: {
            fields:{
                id     : 'empty',
                name: 'empty',
                contact: ['exactLength[10]', 'empty', 'integer'],
                dob: 'empty',
                branch: 'empty',
                category: 'empty'
            }
        },
        studentModal: {
            closable: false,
            onDeny    : function(){
                return true
            },
            onApprove : function(){
                return app.studentModalOnApprove()
            }
        },
    },
    created: function(){
        console.log('created')
        this.loadv2([
            {name:'Students',
             url:'/api/student/all',
             variableName: 'students',
             dataInReponse: 'students'},
            {name:'Categories',
             url:'/api/category/list',
             variableName: 'categories',
             dataInReponse: 'categories'},
            {name:'Branches',
             url:'/api/branch/list',
             variableName: 'branches',
             dataInReponse: 'branches'}
             ])
    },
    updated: function(){
        console.log('updated')
        if(!this.initialized && !this.loading){
            var vm = this
            console.log('initialized')
            $(this.$el).find('table').tablesort()
            $(this.$el).find('.dropdown').dropdown()
            this.initialized = true
            $(this.$el).find('#addStudentForm').form(this.studentForm)
            $(this.$el).find('#studentModal').modal(this.studentModal)
        }
    },
    methods: {
        studentModalOnApprove: function() {
            console.log('studentModalOnApprove')
            $('#addStudentForm').form('validate form')
            this.addOrUpdateStudent()
            return false
        },
        importStudents: function(){
            this.importing = true;
            console.log('importing students from', this.importFile)
                //send the file to server and get list new students 
                //and list of updating students
                var vm = this;
                var url = '/api/admin/student/import'
                var postData = new FormData()
                postData.append('studentsListFile',this.importFile)
                vm.$http.post(url, postData)
                .then(response => {
                    console.log(response)
                    if(response.body.status=='success'){
                        //for showing summary of import
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
                            // refresh the modal to set it in center
                        }, 200)
                        if(response.body.added.length > 0 || response.body.updated.length > 0)
                            vm.loadStudents();
                            // reload the student in actual list
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
                        if(response.body.statusText && response.body.statusData){
                            var errorMessage = this.constructErrorMessage(response.body.statusText, response.body.statusData)
                            if(errorMessage){
                                $('#addStudentForm').form('add errors', [errorMessage])
                            }
                        }
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
                        vm.showToast('Student added successfuly', 'success')
                    }
                    $('#studentModal').modal('hide')
                    //get the new data from response and add him to the students list
                }, error => {
                    console.log(error)
                    vm.loading = ''
                })
            },
            updateStudent (id) {
                console.log(id)
                $('#addStudentForm').form('reset')
                $('#addStudentForm .message').empty()
                if(id == -1){
                    $('#addStudentForm :input[name="id"]').attr('disabled', false)
                    this.resetStudent()
                    $('#studentModal').modal('show')
                    return
                }
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
                $('#addStudentForm :input[name="category"]').dropdown('set selected', stdToUpdate.category)
                $('#addStudentForm :input[name="branch"]').dropdown('set selected', stdToUpdate.branch)
                $('#addStudentForm :input[name="id"]').attr('disabled', true)
                $('#studentModal').modal('show')
            },
            resetStudent: function(){
                // clear the drop down and reset the studentToUpdate
                $('#addStudentForm select').dropdown('clear')
                this.studentToUpdate = {}
                this.isUpdate = false
                $('#addStudentForm').form('reset')
            },
            getJsonFromForm: function(formSelector){
                data = {}
                $(formSelector).find(':input').each(function(index, input){
                    data[input.name] = input.value
                    input.value = ''
                })
                return data
            },
            showImportModal(){
                $('#importModal').modal('show')
            },
            hideImportModal(){
                $('#importModal').modal('hide')
                this.clearImportState()
            },
            clearImportState(){
                this.loadedStudents = []
                this.importing = ''
                this.imported = false
                this.importSummary = ''
            },
            // Form validation prompts
            prmptStdId(newId){
                console.log('validating...', newId)
                if(!newId){
                    return 'Student ID cannot be blank'
                }
                var found = 0
                this.students.forEach((student, index) => {
                    if (student.student_id === newId)
                        found += 1
                })
                return found == 0 ? undefined : "Student ID already assigned, choose another!"
            }
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
            filteredStudents(){
                var vm = this
                var lowerTxt = this.searchTxt.toLowerCase()
                var students = this.students.filter(student => {
                    return (vm.categoryFilter.length == 0 || vm.categoryFilter.indexOf(student.category) != -1) &&
                    ( vm.branchFilter.length == 0 || vm.branchFilter.indexOf(student.branch) != -1) &&
                    ( vm.statusFilter == 'all' || vm.statusFilter == student.active+'') &&
                    ( student.name.toLowerCase().indexOf(lowerTxt) != -1 ||
                      this.getCategoryName(student.category).toLowerCase().indexOf(lowerTxt) != -1 ||
                      this.getBranchName(student.branch).toLowerCase().indexOf(lowerTxt) != -1
                      )
                })
                students.sort(function(s1, s2){
                    var s1a = s1.active || false
                    var s2a = s2.active || false
                    if(s1a === s2a){
                        s1a = vm.getCategoryName(s1.category) || '' 
                        s2a = vm.getCategoryName(s2.category) || ''
                        if(s1a === s2a){
                            s1a = s1.name || ''
                            s2a = s2.name || ''
                            s1a = s1a.toLowerCase()
                            s2a = s2a.toLowerCase()
                            if (s1a === s2a)
                                return 0
                            return s1a > s2a ? 1 : -1
                        }else{
                            return s1a > s2a ? 1 : -1
                        }
                    } else {
                        return s2a - s1a                         
                    }
                })
                return students
            }
        },
    });