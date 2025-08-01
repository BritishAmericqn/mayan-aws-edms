��          �      \      �  �   �     \     p  E   �     �  .   �  8   �  �   3  
          
   "     -     2     6     F     U  /   f     �  ]   �  �  �  �   �  (   �       ?  &     f	  r   s	  �   �	  v  g
     �  
   �          '     0     4     R  (   g  T   �     �  n   �                                         
                	                                          Criteria to use when searching for messages to process. Use the format specified in https://tools.ietf.org/html/rfc2060.html#section-6.4.4 Destination mailbox Execute expunge Execute the IMAP expunge command after processing each email message. Host IMAP Mailbox from which to check for messages. IMAP Mailbox to which processed messages will be copied. IMAP STORE command to execute on messages after they are processed. One command per line. Use the commands specified in https://tools.ietf.org/html/rfc2060.html#section-6.4.6 or the custom commands for your IMAP server. IMAP email Mailbox POP3 email Port SSL Search criteria Store commands Store email body Store the body of the email as a text document. Timeout Typical choices are 110 for POP3, 995 for POP3 over SSL, 143 for IMAP, 993 for IMAP over SSL. Project-Id-Version: Mayan EDMS
Report-Msgid-Bugs-To: 
PO-Revision-Date: 2025-01-20 12:34+0000
Last-Translator: lilo.panic, 2025
Language-Team: Russian (https://app.transifex.com/rosarior/teams/13584/ru/)
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Language: ru
Plural-Forms: nplurals=4; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 || n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3);
 Критерии, которые следует использовать при поиске сообщений для обработки. Используйте формат, указанный в https://tools.ietf.org/html/rfc2060.html#section-6.4.4 Целевой почтовый ящик Выполнить EXPUNGE Выполнить команду EXPUNGE после обработки каждого сообщения электронной почты. Команда EXPUNGE используется для удаления из почтового ящика всех сообщений, помеченных флагом \Deleted Сервер Папка почтового ящика IMAP, в которой нужно проверять сообщения. Почтовый ящик IMAP, в который будут скопированы обработанные сообщения. Команды IMAP STORE, выполняемые для сообщений после их обработки. По одной команде на строку. Используйте команды, указанные в https://tools.ietf.org/html/rfc2060.html#section-6.4.6, или пользовательские команды для вашего сервера IMAP. Почтовый ящик IMAP Папка Почтовый ящик POP3 Порт SSL Критерии поиска Команды STORE Сохранять тело письма Сохранять тело письма как текстовый документ. Тайм-аут Обычно выбирают 110 для POP3, 995 для POP3 с SSL, 143 для IMAP, 993 для IMAP с SSL 