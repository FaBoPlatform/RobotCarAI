
;
input/batch_sizePlaceholder*
dtype0*
shape:
6
	step/stepConst*
dtype0*
valueB
 :���
�
queue/FIFOQueueFIFOQueueV2*
shapes
::*
shared_name *
capacityd*
	container *
component_types
2

queue/dequeue_opQueueDequeueManyV2queue/FIFOQueueinput/batch_size*

timeout_ms���������*
component_types
2
�
neural_network_model/Variable_1Const*
dtype0*�
value�B�"���!?��
? 5?ܽF>�o��R��<��?�}};1����>X��=w��?r� ��Q�?��½A�'?�#�;) �������2<HlоV=J��.�w����>2��?��2@H�&%�?���<Į���-3=
�
$neural_network_model/Variable_1/readIdentityneural_network_model/Variable_1*
T0*2
_class(
&$loc:@neural_network_model/Variable_1
x
neural_network_model/Variable_3Const*
dtype0*A
value8B6",ڠ���2�<�q@����Ei�ܞA��@�׺@@x(A�!�A���
�
$neural_network_model/Variable_3/readIdentityneural_network_model/Variable_3*
T0*2
_class(
&$loc:@neural_network_model/Variable_3
�
neural_network_model/Variable_5Const*
dtype0*�
value�B�"�&z����2?̡�>��	��=x= ��>�ׅ°�#���?�B辫�q=T�z���/�@��B�B�f$��@�=���?6��ȑ��h�@������R@��ܿ��ܿ
�^@^^@C�4@������ʨ�?yg^�^6�@lU?{�-Aˎ������<4��2%���UViA��-�
�
$neural_network_model/Variable_5/readIdentityneural_network_model/Variable_5*
T0*2
_class(
&$loc:@neural_network_model/Variable_5
\
neural_network_model/Variable_7Const*
dtype0*%
valueB"d�A�̴@_zk�=2A
�
$neural_network_model/Variable_7/readIdentityneural_network_model/Variable_7*
T0*2
_class(
&$loc:@neural_network_model/Variable_7
�
neural_network_model/MatMulMatMulqueue/dequeue_op$neural_network_model/Variable_1/read*
T0*
transpose_a( *
transpose_b( 
k
neural_network_model/AddAddneural_network_model/MatMul$neural_network_model/Variable_3/read*
T0
D
neural_network_model/ReluReluneural_network_model/Add*
T0
�
neural_network_model/MatMul_1MatMulneural_network_model/Relu$neural_network_model/Variable_5/read*
T0*
transpose_a( *
transpose_b( 
r
neural_network_model/output_yAddneural_network_model/MatMul_1$neural_network_model/Variable_7/read*
T0
M
neural_network_model/scoreSoftmaxneural_network_model/output_y*
T0 