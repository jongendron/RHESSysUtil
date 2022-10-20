($2 == "n_deposition") {printf("\n%f %s",par,$2);}
($2 != "n_deposition") {printf("\n%s %s",$1,$2);}


