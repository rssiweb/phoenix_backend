var app = new Vue({
        el: '#app',
        data: {
            token: Cookies.get('auth_token'),
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
            addStudent: function(){
                this.loading = 'Adding Student...'
                data = this.getJsonFromForm($('#addStudentForm input'))
                console.log(data);
                this.$http.post('/api/student/add',data,{
                    headers: { Authorization: 'Basic ' +  this.token}
                }).then( response => {
                    console.log(response);
                    //get the new data from response and add him to the students list
                }, error => {
                    console.log(error);
                });
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
                    return "Update Student"       
                else
                    return "Add Student"
            },
            formDate:function(){
                if(this.studentToUpdate.dob)
                    return moment(this.studentToUpdate.dob).format('YYYY-MM-DD');
                else
                    return ''
            }
        }
    });