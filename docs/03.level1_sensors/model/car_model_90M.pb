
;
input/batch_sizePlaceholder*
shape:*
dtype0
6
	step/stepConst*
dtype0*
valueB
 :���*
�
queue/FIFOQueueFIFOQueueV2*
component_types
2*
shapes
::*
shared_name *
capacityd*
	container 

queue/dequeue_opQueueDequeueManyV2queue/FIFOQueueinput/batch_size*

timeout_ms���������*
component_types
2
�
neural_network_model/Variable_1Const*
dtype0*�
value�B�"��Շ?�?"�+?9�.>�B���s&=���?��;O�'�0$>��=\�!@`"׺�i`?�跼��k?��F<g�S�����<������<��=F��8R�ԓ�=�2�?vؾ<E��B�?I�y�T�EQ�=
�
$neural_network_model/Variable_1/readIdentityneural_network_model/Variable_1*
T0*2
_class(
&$loc:@neural_network_model/Variable_1
x
neural_network_model/Variable_3Const*
dtype0*A
value8B6",����5=C�A�2���-=i�@�@ %A��IA�7�A�i��
�
$neural_network_model/Variable_3/readIdentityneural_network_model/Variable_3*
T0*2
_class(
&$loc:@neural_network_model/Variable_3
�
neural_network_model/Variable_5Const*
dtype0*�
value�B�"�
��t?n��>�%���;���.7���¶ٽ>[��?	�F�NO�{E��r\E�(��@^F��v�$��I�����9@1�?�b@��\AES��.��@� �g@�H��@��b@C�@@���������?����eA'5�����AVcʿ�{����4$M�b,Z�l%�A��X�
�
$neural_network_model/Variable_5/readIdentityneural_network_model/Variable_5*
T0*2
_class(
&$loc:@neural_network_model/Variable_5
\
neural_network_model/Variable_7Const*
dtype0*%
valueB"�B�+A�L����MA
�
$neural_network_model/Variable_7/readIdentityneural_network_model/Variable_7*
T0*2
_class(
&$loc:@neural_network_model/Variable_7
�
neural_network_model/MatMulMatMulqueue/dequeue_op$neural_network_model/Variable_1/read*
transpose_b( *
T0*
transpose_a( 
k
neural_network_model/AddAddneural_network_model/MatMul$neural_network_model/Variable_3/read*
T0
D
neural_network_model/ReluReluneural_network_model/Add*
T0
�
neural_network_model/MatMul_1MatMulneural_network_model/Relu$neural_network_model/Variable_5/read*
transpose_a( *
transpose_b( *
T0
r
neural_network_model/output_yAddneural_network_model/MatMul_1$neural_network_model/Variable_7/read*
T0
M
neural_network_model/scoreSoftmaxneural_network_model/output_y*
T0 