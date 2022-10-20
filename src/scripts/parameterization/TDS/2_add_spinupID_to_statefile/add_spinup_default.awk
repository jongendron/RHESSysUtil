-{a=0;} 
-($2=="cover_fraction") {printf("%f	%s\n%f	%s\n",1.0,"spinup_object_ID",$1,$2); a=1;}
-(a == 0) {printf("%s	%s\n",$1,$2);}
\ No newline at end of file

