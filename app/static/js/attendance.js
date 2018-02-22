var app = new Vue({
        el: '#app',
        data: {
            heading:'Attendance',
            token: Cookies.get('auth_token'),
            students: [],
            error: '',
            message: '',
            loading: '',
            timeFormat: '',
            attendanceDate: moment(),
            displayDateString: moment().format('dddd, Do MMMM'),
            isToday: true,
            viewOnly: false,
        },
        created: function(){
            console.log('stating');
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
                        this.getAttendance();
                    },error => {
                        this.error = error.body.message;
                        console.log(error);
                        this.loading = '';
                    });
            },
            getAttendance: function(){
                this.loading = 'Loading attendance...'
                var token = this.token
                var vm = this
                this.$http.get('/api/attendance/'+this.attendanceDate.format('DDMMYYYY'),{
                        headers: { Authorization: 'Basic ' +  token}
                    }).then(data => {
                        var students = vm.students;
                        data.body.attendance.forEach(function(item, index){
                            //TODO: updated attendance of students
                            students.forEach(function(student, stdi){
                                if(student.id == item.student.id){
                                    console.log(student,item,'matched');
                                    student.in = item.punchIn;
                                    student.out = item.punchOut;
                                    student.comment = item.comments;
                                    vm.$set(vm.students, index, student);
                                }
                            })
                        });
                        this.loading = '';
                    },error => {
                        console.log(error);
                        this.loading = '';
                        this.message = error.data.message;
                    });
            },
            saveAttendance:function(){
                this.loading = 'Saving attendance..';
                var updatedStudents = [];
                $(this.students).each(function(index, student){
                    if(student.in && student.out)
                        updatedStudents.push({
                            student_id: student.id,
                            in: student.in,
                            out: student.out,
                            comment: student.comment
                        });
                });
                this.$http.post('/api/attendance/set/' + moment(this.attendanceDate).format('DDMMYYYY'), updatedStudents, {
                    headers: { Authorization: 'Basic ' +  this.token}
                }).then( response => {
                    console.log(response);
                    this.loading = '';
                }, error => {
                    console.log(error);
                    this.loading = '';    
                });
            },
            punchIn: function(student){
                var updatedStd = student;
                if(!student.in){
                    updatedStd.in = new Date();
                }
                else{
                    updatedStd.in = undefined;
                    updatedStd.out = undefined;
                }
                this.$set(this.students, this.students.indexOf(student), updatedStd);
                //ajax request to punch in the student
                this.$http.post('/api/attendance/punchin/'+moment(this.attendanceDate).format('DDMMYYYY')+'/'+student.id,{in: moment(student.in).format('HH:mm:ss')},{
                    headers: { Authorization: 'Basic ' +  this.token}
                }).then(response => {
                    console.log(response);
                }, error => {
                    console.log(error);
                });
            },
            punchOut: function(student){
                var updatedStd = student;
                if(!student.out)
                    updatedStd.out = new Date();
                else
                    updatedStd.out = undefined;
                this.$set(this.students, this.students.indexOf(student), updatedStd);
                console.log(this.students);
            },
            getPresentableTime: function(datetime){
                return moment(datetime).format('hh mm:ss A');
            },
            nextDay: function(){
                console.log('nextDay');
                this.attendanceDate.add(1, 'day');
                this.displayDateString = this.attendanceDate.format('dddd, Do MMMM');
            },
            previousDay: function(){
                console.log('preDay');
                this.attendanceDate.subtract(1, 'day');
                this.displayDateString = this.attendanceDate.format('dddd, Do MMMM');
                this.viewOnly = true;
                this.getAttendance();
                
            }
        },
        watch:{
            token: function(){
                if(!this.token)
                    window.location = '/';
            },
            attendanceDate: function(){
                this.isToday = moment(this.attendanceDate.format('YYYY-MM-DD')).isAfter(moment())
            }
        },
        computed:{
            
        }
    });