% translate statements to statements_holprefix
%
% /usr/bin/swipl -f tptp2prefix.pl <statements > statements_holprefix

% untested -- for newer swi
declare_TPTP_operators :-
    op(99,fx,'$'),
    op(100,fx,++),
    op(100,fx,--),
    op(100,xf,'!'),
    op(400,fx,'^'),
    op(405,xfx,'='),
    op(405,xfx,'~='),
    op(450,fy,~),
    op(501,yfx,'@'),
    (system_mode(true),op(502,xfy,'|'),system_mode(false)),
    op(502,xfy,'~|'),
    op(503,xfy,&),
    op(503,xfy,~&),
    op(504,xfy,=>),
    op(504,xfy,<=),
    op(505,xfy,<=>),
    op(505,xfy,<~>),
%----! and ? are of higher precedence than : so !X:p(X) is :(!(X),p(X))
%----Otherwise !X:!Y:p(X,Y) cannot be parsed.
    op(400,fx,!),
    op(400,fx,?),
%----Need : stronger than + for equality and otter in tptp2X
%----Need : weaker than quantifiers for !X : ~p
    op(450,xfy,:),
%---- .. used for range in tptp2X. Needs to be stronger than :
    op(400,xfx,'..').

tr($true) :- !, write('$true'), write(' ').
tr($false) :- !, write('$false'), write(' ').
tr('$VAR'(V)) :- !, write('X'), write(V), write(' ').
tr(':'('!'([X]),QF)) :- !, write('! '), tr(X), tr(QF).
tr(':'('?'([X]),QF)) :- !, write('? '), tr(X), tr(QF).
tr(':'('!'([X|Xs]),QF)) :- !,write('! '), tr(X), tr(':'('!'(Xs),QF)).
tr(':'('?'([X|Xs]),QF)) :- !,write('? '), tr(X), tr(':'('?'(Xs),QF)).
tr(F) :-
    F=..[C|As],
    writeapps(As,N),
    write(C), write('__'), write(N), write(' '),
    maplist(tr,As). %maplist is same as checklist, but the latter is deprecated

%writeapps(_).
writeapps([],0).
writeapps([_|T],N):- writeapps(T,NT), N is NT + 1.

%translate(fof(N,_,F)) :- numbervars(F,0,_),write(N),write(' '),tr(F).

translate(F) :- numbervars(F,1,_),tr(F).

:- declare_TPTP_operators,
   repeat, (read(X),X\=end_of_file -> translate(X), nl ; halt), fail.

