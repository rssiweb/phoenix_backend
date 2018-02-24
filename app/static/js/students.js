var app = new Vue({
        el: '#app',
        data: {
            heading: 'Students',
            token: Cookies.get('auth_token'),
            is_admin: (Cookies.get('is_admin')=='true'),
            students: [],
            error: '',
            message: '',
            loading: '',
            studentToUpdate: {},
            isUpdate: false,
        },
        created: function(){
            this.loadStudents();
        },
        methods: {
            logout: function(){
                Cookies.remove('auth_token');
                window.location = '/';
            },
            getHeaders: function(){
                return {headers: { Authorization: 'Basic ' +  this.token}}
            },
            loadStudents: function(){
                this.loading = 'Loading students...'
                var token = this.token;
                console.log('token', token);
                this.$http.get('/api/student',{
                        headers: { Authorization: 'Basic ' +  token}
                    }).then(data => {
                        console.log(data);
                        this.students = data.body.students
                        if(this.students.length == 0){
                        if(data.body.message)
                                this.message = data.body.message;
                            else
                                this.message = 'No students';
                        }else{
                            this.message = '';
                        }
                        console.log(this.message);
                        this.loading = '';
                    },error => {
                        this.error = error.body.message;
                        console.log(error);
                        this.loading = '';
                    });
            },
            addOrUpdateStudent: function(){
                this.error = ''
                var url = '';
                if(this.studentToUpdate){
                    this.loading = 'Updating '+this.studentToUpdate.name+'...'
                    url = '/api/student/update';
                }
                else{
                    this.loading = 'Adding '+$('#addStudentForm input[name="name"]').val()+'...'
                    url = '/api/student/add';
                }

                postData = this.getJsonFromForm($('#addStudentForm input'))
                console.log(postData);
                var vm = this
                
                this.$http.post(url, postData, vm.getHeaders())
                .then( response => {
                    console.log(response);
                    vm.loading = '';
                    if(response.body.status=='fail'){
                        vm.error = response.body.message;
                        return;
                    }
                    // reset only if its success
                    vm.resetStudent()
                    var updatedStudent = response.body.student;
                    console.log(updatedStudent);
                    if(!updatedStudent) return;

                    var indexToreplace = -1;
                    vm.students.forEach((tmpstd, index) => {
                        if(tmpstd.id == updatedStudent.id){
                            indexToreplace = index;
                            console.log(index);
                        }
                    });
                    if(indexToreplace != -1){
                        vm.$set(vm.students, indexToreplace, updatedStudent)
                        console.log('setted');
                    }else{
                        vm.students.push(updatedStudent);
                    }
                    //get the new data from response and add him to the students list
                }, error => {
                    console.log(error);
                    vm.loading = '';
                });
            },
            deleteStudent:function(student){
                console.log('delete', student);
                this.loading = 'Deleting '+student.name+'...'
                var vm = this;
                var url = '/api/student/delete/'+student.id
                this.$http.get(url,this.getHeaders())
                .then(response => {
                    console.log(response);    
                    this.loading = ''
                    if(response.body.status=='success'){
                        //remove the student from list
                        vm.resetStudent();
                        var removedStudentIndex = -1;
                        vm.students.forEach((tmpStd, index) => {
                            if(tmpStd.id == response.body.studentid){
                                removedStudentIndex = index;
                            }
                        });
                        if(removedStudentIndex!=-1)
                            vm.students.splice(removedStudentIndex, 1);
                    }
                },
                error => {
                    console.log(error);
                    this.loading = ''
                })
            },
            updateStudent: function(id){
                console.log(id);
                var stdToUpdate = null;
                this.students.forEach(function(student, index){
                    if(student.id == id){
                        stdToUpdate = student;
                    }
                });
                if(!stdToUpdate) return;
                this.isUpdate= true;
                this.studentToUpdate = jQuery.extend({}, stdToUpdate);
            },
            resetStudent: function(){
                this.studentToUpdate = {};
                this.isUpdate = false;
                $('#addStudentForm input').each(function(index,input){
                    input.value ='';
                })
            },
            getJsonFromForm: function(formInputArr){
                data = {}
                $(formInputArr).each(function(index, input){
                    data[input.name] = input.value;
                    input.value = '';
                });
                return data;
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
                    return moment(this.studentToUpdate.dob).format('YYYY-MM-DD');
                else
                    return ''
            }
        }
    });