
;
input/batch_sizePlaceholder*
dtype0*
shape:
6
	step/stepConst*
dtype0*
valueB
 :���9
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
component_types
2*

timeout_ms���������
�
neural_network_model/Variable_1Const*
dtype0*�
value�B�"�8�?L�?�V8?��>,��T[V=�б?Y�`;��%���m=��=YRQ@�-%���D?�!�;J�f?���<EĿ��	M=�,�C�8=��?@����\���=4�?�����|�� 8�?�!�HE�=���=
�
$neural_network_model/Variable_1/readIdentityneural_network_model/Variable_1*
T0*2
_class(
&$loc:@neural_network_model/Variable_1
x
neural_network_model/Variable_3Const*
dtype0*A
value8B6",�%��F�C=>�3A"����Q?���@�V�@n�	A/?PAzr�AYp��
�
$neural_network_model/Variable_3/readIdentityneural_network_model/Variable_3*
T0*2
_class(
&$loc:@neural_network_model/Variable_3
�
neural_network_model/Variable_5Const*
dtype0*�
value�B�"�Y*��Y|i?�\y>^뾎Y�q_��p������?J��?b�z���E�'���U�b�<�@쾨������A�}�<�,j@\�]?[n0@�hA�������@2���w��ɹ@q@0JP@V�~��\��Z��M�Au1��>�Ak��:2�R/\���S��
d��Q�A!�^�
�
$neural_network_model/Variable_5/readIdentityneural_network_model/Variable_5*
T0*2
_class(
&$loc:@neural_network_model/Variable_5
\
neural_network_model/Variable_7Const*
dtype0*%
valueB"%wBJD@ATܹ���eA
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